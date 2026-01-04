"""
Leaderboard routes for F1-Score Grand Prix
Flask version matching FastAPI behavior
"""

from flask import Blueprint, jsonify

from database.models import Submission

leaderboard_bp = Blueprint("leaderboard", __name__)


def _submission_to_dict(submission):
    """Convert submission model to dict."""
    return {
        "submission_id": submission.id,
        "task_id": submission.task_id,
        "score": submission.score if submission.score is not None else 0,
        "timestamp": submission.created_at.isoformat() if submission.created_at else None,
        "status": submission.status,
        "team_name": submission.team_name,
        "filename": submission.filename,
    }


@leaderboard_bp.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    """Return leaderboard backed by SQLite (top 20 per task)."""
    submissions = Submission.query.all()

    by_task = {}
    for task_id in range(4):
        task_subs = (
            Submission.query
            .filter(Submission.task_id == task_id, Submission.status == "success")
            .order_by(Submission.score.desc(), Submission.created_at.asc())
            .limit(20)
            .all()
        )
        by_task[str(task_id)] = [_submission_to_dict(s) for s in task_subs]

    return jsonify({
        "submissions": [_submission_to_dict(s) for s in submissions],
        "by_task": by_task,
    })
