"""
Flask configuration for F1-Score Grand Prix ML Competition Platform
"""

import os
from pathlib import Path
from datetime import timedelta


class Config:
    """Base configuration."""
    
    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "change-this-secret-key"))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60 * 24)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    
    # Database
    BACKEND_DIR = Path(__file__).parent
    DB_PATH = (BACKEND_DIR / "database" / "db.sqlite3").as_posix()
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Paths
    DATA_DIR = BACKEND_DIR / "data"
    SUBMISSIONS_DIR = BACKEND_DIR / "submissions"
    TEMPLATES_DIR = BACKEND_DIR / "templates"
    
    # Submission limits
    SUBMISSION_LIMIT_PER_TASK = 3
