from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database path (local to the backend folder)
DB_PATH = (Path(__file__).resolve().parent / "db.sqlite3").as_posix()
DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False allows usage across FastAPI threads
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
