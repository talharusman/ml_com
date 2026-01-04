"""
Flask backend for F1-Score Grand Prix ML Competition Platform
"""

import os
from pathlib import Path

from flask import Flask

from config import Config
from extensions import db, jwt, cors


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure directories exist
    Path(app.config.get("SUBMISSIONS_DIR", "submissions")).mkdir(exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.tasks import tasks_bp
    from routes.submissions import submissions_bp
    from routes.leaderboard import leaderboard_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(submissions_bp)
    app.register_blueprint(leaderboard_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    print("Starting F1-Score Grand Prix backend on http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=True)
