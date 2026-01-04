"""
Authentication routes for F1-Score Grand Prix
Flask version matching FastAPI behavior
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from passlib.context import CryptContext

from extensions import db
from database.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    data = request.get_json()
    
    if not data:
        return jsonify({"detail": "Invalid request body"}), 400
    
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    
    if not username or not password:
        return jsonify({"detail": "Username and password are required"}), 400
    
    # Check for existing username
    existing = User.query.filter_by(username=username).first()
    if existing:
        return jsonify({"detail": "Username already registered"}), 400
    
    # Check for existing email
    if email:
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({"detail": "Email already registered"}), 400
    
    # Create new user
    db_user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
    )
    db.session.add(db_user)
    db.session.commit()
    
    # Generate token
    token = create_access_token(identity=db_user.id)
    
    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email},
    })


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login user and return JWT token."""
    # Support both form data and JSON
    if request.content_type and "application/x-www-form-urlencoded" in request.content_type:
        username = request.form.get("username")
        password = request.form.get("password")
    else:
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")
    
    if not username or not password:
        return jsonify({"detail": "Username and password are required"}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(password, user.hashed_password):
        return jsonify({"detail": "Incorrect username or password"}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token, "token_type": "bearer"})


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def read_users_me():
    """Get current user info."""
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
    })
