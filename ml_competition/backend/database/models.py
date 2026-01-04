"""
Database models for F1-Score Grand Prix
Using Flask-SQLAlchemy
"""

import uuid
from datetime import datetime

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String, unique=True, nullable=False, index=True)
    email = db.Column(db.String, unique=True, nullable=True, index=True)
    hashed_password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship("Submission", back_populates="user")


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String, unique=True, nullable=False, index=True)
    contact_email = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship("Submission", back_populates="team")


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4())[:8])
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=True)
    team_id = db.Column(db.String, db.ForeignKey("teams.id"), nullable=True)
    team_name = db.Column(db.String, nullable=True)
    task_id = db.Column(db.Integer, nullable=False, index=True)
    filename = db.Column(db.String, nullable=False)
    storage_path = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default="uploaded", nullable=False)
    score = db.Column(db.Float, nullable=True)
    details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship("User", back_populates="submissions")
    team = db.relationship("Team", back_populates="submissions")
