"""
FastAPI backend for F1-Score Grand Prix ML Competition Platform
"""

import os
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from evaluator import evaluate_submission
from utils import load_task_info, generate_submission_id
from database.session import Base, engine, get_db
from database.models import Submission, Team, User

# Initialize FastAPI app
app = FastAPI(title="F1-Score Grand Prix", version="1.0.0")

# CORS: allow all origins for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple JWT auth settings (replace SECRET_KEY in production)
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
bearer_scheme = HTTPBearer(auto_error=False)

# Paths
BACKEND_DIR = Path(__file__).parent
DATA_DIR = BACKEND_DIR / "data"
SUBMISSIONS_DIR = BACKEND_DIR / "submissions"
# Serve static frontend from ../frontend/static
FRONTEND_STATIC_DIR = BACKEND_DIR.parent / "frontend" / "static"
# Create directories if they don't exist
SUBMISSIONS_DIR.mkdir(exist_ok=True)
FRONTEND_STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory=str(FRONTEND_STATIC_DIR)), name="static")


@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    """Handle CORS preflight requests explicitly."""
    return Response(status_code=200)


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    username: str
    email: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    return db.query(User).filter(User.id == user_id).first()


def _get_or_create_team(db: Session, team_name: str) -> Optional[Team]:
    if not team_name:
        return None
    team = db.query(Team).filter(Team.name == team_name).first()
    if team:
        return team
    team = Team(name=team_name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def _submission_to_dict(submission: Submission) -> dict:
    return {
        "submission_id": submission.id,
        "task_id": submission.task_id,
        "score": submission.score if submission.score is not None else 0,
        "timestamp": submission.created_at.isoformat() if submission.created_at else None,
        "status": submission.status,
        "team_name": submission.team_name,
        "filename": submission.filename,
    }


# Max submissions allowed per team per task
SUBMISSION_LIMIT_PER_TASK = 3


@app.post("/auth/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    if user.email:
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    token = create_access_token({"sub": db_user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email},
    }


@app.post("/auth/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserOut(id=current_user.id, username=current_user.username, email=current_user.email)


@app.get("/")
async def serve_home():
    """Serve homepage (index.html)"""
    return FileResponse(FRONTEND_STATIC_DIR / "index.html", media_type="text/html")


@app.get("/tasks")
async def get_tasks():
    """Return list of all tasks with descriptions"""
    tasks = load_task_info()
    return JSONResponse(tasks)


@app.get("/download/{task_id}")
async def download_training_data(task_id: str):
    """Download training CSV for a given task"""
    try:
        task_id_int = int(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task_id")
    
    if task_id_int not in range(4):
        raise HTTPException(status_code=404, detail="Task not found")
    
    train_path = DATA_DIR / f"task{task_id_int}_train.csv"
    
    if not train_path.exists():
        raise HTTPException(status_code=404, detail="Training data not found")
    
    return FileResponse(
        train_path,
        media_type="text/csv",
        filename=f"task{task_id_int}_train.csv"
    )


@app.post("/upload/{task_id}")
async def upload_submission(
    task_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Accept and save uploaded submission.py file"""
    try:
        task_id_int = int(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task_id")
    
    if task_id_int not in range(4):
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="File must be a Python (.py) file")

    # Determine team name before any disk writes
    team_name = current_user.username if current_user else file.filename.replace(".py", "")
    team = _get_or_create_team(db, team_name)

    # Enforce submission limit per team per task before saving file
    if team:
        existing_count = (
            db.query(Submission)
            .filter(Submission.team_id == team.id, Submission.task_id == task_id_int)
            .count()
        )
        if existing_count >= SUBMISSION_LIMIT_PER_TASK:
            raise HTTPException(
                status_code=400,
                detail=f"Submission limit reached for this task (max {SUBMISSION_LIMIT_PER_TASK}). You already submitted {existing_count} time(s).",
            )

    # Generate unique submission ID and save file
    submission_id = generate_submission_id()
    safe_filename = f"task{task_id_int}_{submission_id}.py"
    submission_path = SUBMISSIONS_DIR / safe_filename

    # Save file to disk
    content = await file.read()
    with open(submission_path, "wb") as f:
        f.write(content)

    submission = Submission(
        id=submission_id,
        user_id=current_user.id if current_user else None,
        team_id=team.id if team else None,
        team_name=team.name if team else None,
        task_id=task_id_int,
        filename=safe_filename,
        storage_path=str(submission_path),
        status="uploaded",
    )
    db.add(submission)
    db.commit()

    return JSONResponse({
        "submission_id": submission_id,
        "task_id": task_id_int,
        "filename": safe_filename,
        "team_name": submission.team_name,
        "status": "uploaded"
    })


@app.post("/evaluate/{submission_id}")
async def evaluate_submission_endpoint(submission_id: str, task_id: int, db: Session = Depends(get_db)):
    """Evaluate a submitted solution and return score"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    submission_file = Path(submission.storage_path)
    if not submission_file.exists():
        # fallback to legacy pattern if path missing
        for file in SUBMISSIONS_DIR.glob(f"*_{submission_id}.py"):
            submission_file = file
            break
    if not submission_file.exists():
        raise HTTPException(status_code=404, detail="Submission file not found")

    try:
        result = evaluate_submission(submission_file, task_id)
        submission.score = result.get("score", 0)
        submission.status = result.get("status", "error")
        submission.details = result.get("details")
        submission.task_id = task_id
        db.commit()
        return JSONResponse(result)
    except Exception as e:
        submission.status = "error"
        submission.score = 0
        submission.details = {"error": str(e)}
        db.commit()
        return JSONResponse({
            "submission_id": submission_id,
            "task_id": task_id,
            "score": 0,
            "status": "error",
            "error": str(e)
        })


@app.get("/leaderboard")
async def get_leaderboard(db: Session = Depends(get_db)):
    """Return leaderboard backed by SQLite (top 20 per task)."""
    submissions = db.query(Submission).all()

    by_task = {}
    for task_id in range(4):
        task_subs = (
            db.query(Submission)
            .filter(Submission.task_id == task_id, Submission.status == "success")
            .order_by(Submission.score.desc(), Submission.created_at.asc())
            .limit(20)
            .all()
        )
        by_task[str(task_id)] = [_submission_to_dict(s) for s in task_subs]

    return JSONResponse({
        "submissions": [_submission_to_dict(s) for s in submissions],
        "by_task": by_task,
    })


@app.get("/template/{task_id}")
async def get_template(task_id: str):
    """New endpoint to fetch template code as text (not file)"""
    try:
        task_id_int = int(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task_id")
    
    if task_id_int not in range(4):
        raise HTTPException(status_code=404, detail="Task not found")
    
    template_path = BACKEND_DIR / "templates" / f"task{task_id_int}_template.py"
    
    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Template not found")
    
    with open(template_path, "r") as f:
        template_code = f.read()
    
    return JSONResponse({
        "task_id": task_id_int,
        "code": template_code
    })


@app.get("/sample-data/{task_id}")
async def get_sample_data(task_id: str):
    """New endpoint to fetch sample data preview (first 100 rows)"""
    try:
        task_id_int = int(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task_id")
    
    if task_id_int not in range(4):
        raise HTTPException(status_code=404, detail="Task not found")
    
    train_path = DATA_DIR / f"task{task_id_int}_train.csv"
    
    if not train_path.exists():
        raise HTTPException(status_code=404, detail="Training data not found")
    
    # Load first 100 rows and sanitize values for JSON
    df = pd.read_csv(train_path, nrows=100)
    # Replace non-finite values with NaN for uniform handling
    df = df.replace([np.inf, -np.inf], np.nan)

    def _sanitize_value(v):
        if v is None:
            return None
        # Map NaN to None
        try:
            if isinstance(v, float) and math.isnan(v):
                return None
        except Exception:
            pass
        # Convert numpy scalars to python types
        if isinstance(v, (np.floating, np.integer)):
            return v.item()
        # Convert pandas timestamps
        if isinstance(v, pd.Timestamp):
            return v.isoformat()
        return v

    records = []
    for row in df.head(100).to_dict(orient='records'):
        clean_row = {k: _sanitize_value(v) for k, v in row.items()}
        records.append(clean_row)

    payload = {
        "task_id": task_id_int,
        "shape": [int(len(df)), int(len(df.columns))],
        "columns": [str(c) for c in df.columns.tolist()],
        "data": records,
    }
    return JSONResponse(jsonable_encoder(payload))

if __name__ == "__main__":
    import uvicorn
    print("Starting F1-Score Grand Prix backend on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
