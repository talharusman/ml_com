"""
FastAPI backend for F1-Score Grand Prix ML Competition Platform
"""

import os
import json
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
from datetime import datetime

from evaluator import evaluate_submission
from utils import load_task_info, generate_submission_id

# Initialize FastAPI app
app = FastAPI(title="F1-Score Grand Prix", version="1.0.0")

# Paths
BACKEND_DIR = Path(__file__).parent
DATA_DIR = BACKEND_DIR / "data"
SUBMISSIONS_DIR = BACKEND_DIR / "submissions"
STATIC_DIR = BACKEND_DIR / "static"
LEADERBOARD_FILE = BACKEND_DIR / "leaderboard.json"

# Create directories if they don't exist
SUBMISSIONS_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

# Initialize leaderboard if not present
if not LEADERBOARD_FILE.exists():
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump({"submissions": []}, f)

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def serve_home():
    """Serve homepage (index.html)"""
    return FileResponse(STATIC_DIR / "index.html", media_type="text/html")


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
async def upload_submission(task_id: str, file: UploadFile = File(...)):
    """Accept and save uploaded submission.py file"""
    try:
        task_id_int = int(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task_id")
    
    if task_id_int not in range(4):
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="File must be a Python (.py) file")
    
    # Generate unique submission ID and save file
    submission_id = generate_submission_id()
    team_name = file.filename.replace(".py", "")
    safe_filename = f"task{task_id_int}_{submission_id}.py"
    
    submission_path = SUBMISSIONS_DIR / safe_filename
    
    # Save file
    content = await file.read()
    with open(submission_path, "wb") as f:
        f.write(content)
    
    return JSONResponse({
        "submission_id": submission_id,
        "task_id": task_id_int,
        "filename": safe_filename,
        "status": "uploaded"
    })


@app.post("/evaluate/{submission_id}")
async def evaluate_submission_endpoint(submission_id: str, task_id: int):
    """Evaluate a submitted solution and return score"""
    submission_file = None
    for file in SUBMISSIONS_DIR.glob(f"*_{submission_id}.py"):
        submission_file = file
        break
    
    if not submission_file:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Run evaluation
    try:
        result = evaluate_submission(submission_file, task_id)
        
        # Update leaderboard
        with open(LEADERBOARD_FILE, "r") as f:
            leaderboard = json.load(f)
        
        leaderboard["submissions"].append({
            "submission_id": submission_id,
            "task_id": task_id,
            "score": result["score"],
            "timestamp": datetime.now().isoformat(),
            "status": result["status"]
        })
        
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(leaderboard, f, indent=2)
        
        return JSONResponse(result)
    
    except Exception as e:
        return JSONResponse({
            "submission_id": submission_id,
            "task_id": task_id,
            "score": 0,
            "status": "error",
            "error": str(e)
        })


@app.get("/leaderboard")
async def get_leaderboard():
    """Updated to return all tasks leaderboard in one view with grouped results"""
    if not LEADERBOARD_FILE.exists():
        return JSONResponse({"submissions": [], "by_task": {}})
    
    with open(LEADERBOARD_FILE, "r") as f:
        leaderboard = json.load(f)
    
    # Group submissions by task
    by_task = {}
    for task_id in range(4):
        submissions = [
            s for s in leaderboard["submissions"] 
            if s.get("task_id") == task_id
        ]
        submissions.sort(key=lambda x: -x.get("score", 0))
        by_task[str(task_id)] = submissions[:20]  # Top 20 per task
    
    return JSONResponse({
        "submissions": leaderboard["submissions"],
        "by_task": by_task
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
    
    # Load first 100 rows
    df = pd.read_csv(train_path, nrows=100)
    
    return JSONResponse({
        "task_id": task_id_int,
        "shape": [len(df), len(df.columns)],
        "columns": df.columns.tolist(),
        "data": df.head(100).to_dict('records')
    })

if __name__ == "__main__":
    import uvicorn
    print("Starting F1-Score Grand Prix backend on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
