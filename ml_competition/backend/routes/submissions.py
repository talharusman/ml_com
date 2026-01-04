"""
Submissions routes for F1-Score Grand Prix
Flask version matching FastAPI behavior
"""

from pathlib import Path

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

from extensions import db
from database.models import User, Team, Submission
from utils import generate_submission_id
from evaluator import evaluate_submission

submissions_bp = Blueprint("submissions", __name__)


def _get_or_create_team(team_name: str):
    """Get or create a team by name."""
    if not team_name:
        return None
    team = Team.query.filter_by(name=team_name).first()
    if team:
        return team
    team = Team(name=team_name)
    db.session.add(team)
    db.session.commit()
    db.session.refresh(team)
    return team


def _get_current_user_optional():
    """Get current user if JWT is present, else return None."""
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            return User.query.filter_by(id=user_id).first()
    except Exception:
        pass
    return None


@submissions_bp.route("/upload/<task_id>", methods=["POST"])
def upload_submission(task_id):
    """Accept and save uploaded submission.py file."""
    try:
        task_id_int = int(task_id)
    except ValueError:
        return jsonify({"detail": "Invalid task_id"}), 400
    
    if task_id_int not in range(4):
        return jsonify({"detail": "Task not found"}), 404
    
    # Check for file in request
    if "file" not in request.files:
        return jsonify({"detail": "No file uploaded"}), 400
    
    file = request.files["file"]
    if not file.filename:
        return jsonify({"detail": "No file selected"}), 400
    
    if not file.filename.endswith(".py"):
        return jsonify({"detail": "File must be a Python (.py) file"}), 400

    # Get current user (optional)
    current_user = _get_current_user_optional()
    
    # Determine team name before any disk writes
    team_name = current_user.username if current_user else file.filename.replace(".py", "")
    team = _get_or_create_team(team_name)

    # Enforce submission limit per team per task before saving file
    submission_limit = current_app.config.get("SUBMISSION_LIMIT_PER_TASK", 3)
    if team:
        existing_count = Submission.query.filter_by(
            team_id=team.id, task_id=task_id_int
        ).count()
        if existing_count >= submission_limit:
            return jsonify({
                "detail": f"Submission limit reached for this task (max {submission_limit}). You already submitted {existing_count} time(s)."
            }), 400

    # Generate unique submission ID and save file
    submission_id = generate_submission_id()
    safe_filename = f"task{task_id_int}_{submission_id}.py"
    
    submissions_dir = current_app.config.get("SUBMISSIONS_DIR") or Path(__file__).parent.parent / "submissions"
    submissions_dir = Path(submissions_dir)
    submissions_dir.mkdir(exist_ok=True)
    submission_path = submissions_dir / safe_filename

    # Save file to disk
    file.save(submission_path)

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
    db.session.add(submission)
    db.session.commit()

    return jsonify({
        "submission_id": submission_id,
        "task_id": task_id_int,
        "filename": safe_filename,
        "team_name": submission.team_name,
        "status": "uploaded"
    })


@submissions_bp.route("/evaluate/<submission_id>", methods=["POST"])
def evaluate_submission_endpoint(submission_id):
    """Evaluate a submitted solution and return score."""
    task_id = request.args.get("task_id")
    if task_id is None:
        return jsonify({"detail": "task_id query parameter is required"}), 400
    
    try:
        task_id = int(task_id)
    except ValueError:
        return jsonify({"detail": "Invalid task_id"}), 400

    submission = Submission.query.filter_by(id=submission_id).first()
    if not submission:
        return jsonify({"detail": "Submission not found"}), 404

    submission_file = Path(submission.storage_path)
    submissions_dir = current_app.config.get("SUBMISSIONS_DIR") or Path(__file__).parent.parent / "submissions"
    
    if not submission_file.exists():
        # fallback to legacy pattern if path missing
        for file in Path(submissions_dir).glob(f"*_{submission_id}.py"):
            submission_file = file
            break
    
    if not submission_file.exists():
        return jsonify({"detail": "Submission file not found"}), 404

    try:
        result = evaluate_submission(submission_file, task_id)
        submission.score = result.get("score", 0)
        submission.status = result.get("status", "error")
        submission.details = result.get("details")
        submission.task_id = task_id
        db.session.commit()
        return jsonify(result)
    except Exception as e:
        submission.status = "error"
        submission.score = 0
        submission.details = {"error": str(e)}
        db.session.commit()
        return jsonify({
            "submission_id": submission_id,
            "task_id": task_id,
            "score": 0,
            "status": "error",
            "error": str(e)
        })
