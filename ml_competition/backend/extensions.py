"""
Flask extensions initialization for F1-Score Grand Prix
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions without app
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
