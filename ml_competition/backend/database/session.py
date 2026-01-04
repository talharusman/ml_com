"""
Database session utilities for F1-Score Grand Prix
Compatible with Flask-SQLAlchemy patterns
"""

from extensions import db

# Re-export db for compatibility
Base = db.Model
