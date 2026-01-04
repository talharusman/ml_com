"""
Tasks routes for F1-Score Grand Prix
Flask version matching FastAPI behavior
"""

import math
from pathlib import Path

import pandas as pd
import numpy as np
from flask import Blueprint, jsonify, send_file, current_app

from utils import load_task_info

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    """Return list of all tasks with descriptions."""
    tasks = load_task_info()
    return jsonify(tasks)


@tasks_bp.route("/download/<task_id>", methods=["GET"])
def download_training_data(task_id):
    """Download training CSV for a given task."""
    try:
        task_id_int = int(task_id)
    except ValueError:
        return jsonify({"detail": "Invalid task_id"}), 400
    
    if task_id_int not in range(4):
        return jsonify({"detail": "Task not found"}), 404
    
    data_dir = current_app.config.get("DATA_DIR") or Path(__file__).parent.parent / "data"
    train_path = data_dir / f"task{task_id_int}_train.csv"
    
    if not train_path.exists():
        return jsonify({"detail": "Training data not found"}), 404
    
    return send_file(
        train_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"task{task_id_int}_train.csv"
    )


@tasks_bp.route("/template/<task_id>", methods=["GET"])
def get_template(task_id):
    """Fetch template code as text."""
    try:
        task_id_int = int(task_id)
    except ValueError:
        return jsonify({"detail": "Invalid task_id"}), 400
    
    if task_id_int not in range(4):
        return jsonify({"detail": "Task not found"}), 404
    
    templates_dir = current_app.config.get("TEMPLATES_DIR") or Path(__file__).parent.parent / "templates"
    template_path = templates_dir / f"task{task_id_int}_template.py"
    
    if not template_path.exists():
        return jsonify({"detail": "Template not found"}), 404
    
    with open(template_path, "r") as f:
        template_code = f.read()
    
    return jsonify({
        "task_id": task_id_int,
        "code": template_code
    })


@tasks_bp.route("/sample-data/<task_id>", methods=["GET"])
def get_sample_data(task_id):
    """Fetch sample data preview (first 100 rows)."""
    try:
        task_id_int = int(task_id)
    except ValueError:
        return jsonify({"detail": "Invalid task_id"}), 400
    
    if task_id_int not in range(4):
        return jsonify({"detail": "Task not found"}), 404
    
    data_dir = current_app.config.get("DATA_DIR") or Path(__file__).parent.parent / "data"
    train_path = data_dir / f"task{task_id_int}_train.csv"
    
    if not train_path.exists():
        return jsonify({"detail": "Training data not found"}), 404
    
    # Load first 100 rows and sanitize values for JSON
    df = pd.read_csv(train_path, nrows=100)
    # Replace non-finite values with NaN for uniform handling
    df = df.replace([np.inf, -np.inf], np.nan)

    def _sanitize_value(v):
        if v is None:
            return None
        # Map NaN to None
        try:
            if isinstance(v, float) and math.isnan(v):
                return None
        except Exception:
            pass
        # Convert numpy scalars to python types
        if isinstance(v, (np.floating, np.integer)):
            return v.item()
        # Convert pandas timestamps
        if isinstance(v, pd.Timestamp):
            return v.isoformat()
        return v

    records = []
    for row in df.head(100).to_dict(orient='records'):
        clean_row = {k: _sanitize_value(v) for k, v in row.items()}
        records.append(clean_row)

    payload = {
        "task_id": task_id_int,
        "shape": [int(len(df)), int(len(df.columns))],
        "columns": [str(c) for c in df.columns.tolist()],
        "data": records,
    }
    return jsonify(payload)
