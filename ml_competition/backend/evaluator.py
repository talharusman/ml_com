"""
Submission evaluator for F1-Score Grand Prix
Runs submissions safely and computes metrics.
"""

import sys
import importlib.util
import pickle
from pathlib import Path
import pandas as pd
import numpy as np

from utils import safe_run_submission, load_task_data, compute_metrics, validate_preprocessing


def evaluate_submission(submission_path, task_id):
    """
    Evaluate a submitted Python file.
    
    Args:
        submission_path (Path): Path to submitted Python file
        task_id (int): Task ID (0-3)
    
    Returns:
        dict: {score, status, details}
    """
    submission_path = Path(submission_path)
    
    if not submission_path.exists():
        return {"score": 0, "status": "error", "error": "Submission file not found"}
    
    try:
        if task_id == 0:
            return _evaluate_task0(submission_path)
        elif task_id in [1, 2, 3]:
            return _evaluate_task_ml(submission_path, task_id)
        else:
            return {"score": 0, "status": "error", "error": f"Unknown task_id: {task_id}"}
    
    except Exception as e:
        return {"score": 0, "status": "error", "error": str(e)}


def _evaluate_task0(submission_path):
    """
    Evaluate Task 0 (EDA/Preprocessing).
    
    Runs preprocess_data(df) and validates output.
    """
    try:
        # Load training data
        df_train = load_task_data(0, "train")
        
        # Import and run preprocessing function
        spec = importlib.util.spec_from_file_location("submission", submission_path)
        submission_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(submission_module)
        
        # Call preprocess_data
        df_processed = submission_module.preprocess_data(df_train.copy())
        
        # Validate preprocessing
        score, details = validate_preprocessing(df_train, df_processed)
        
        return {
            "score": score,
            "status": "success",
            "details": details
        }
    
    except Exception as e:
        return {
            "score": 0,
            "status": "error",
            "error": f"Task 0 evaluation failed: {str(e)}"
        }


def _evaluate_task_ml(submission_path, task_id):
    """
    Evaluate Tasks 1-3 (ML tasks).
    
    Runs train_model() and evaluate_model() functions.
    """
    try:
        # Load training and test data
        df_train = load_task_data(task_id, "train")
        df_test = load_task_data(task_id, "test")
        
        # Split features and target (assume last column is 'target')
        X_train = df_train.drop(columns=["target"])
        y_train = df_train["target"]
        X_test = df_test.drop(columns=["target"])
        y_test = df_test["target"]
        
        # Import and run model functions
        spec = importlib.util.spec_from_file_location("submission", submission_path)
        submission_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(submission_module)
        
        # Train model
        model = submission_module.train_model(X_train, y_train)
        
        # Evaluate model
        score = submission_module.evaluate_model(model, X_test, y_test)
        
        # Ensure score is a float between 0-1
        score = float(score)
        score = max(0, min(1, score))
        
        return {
            "score": round(score, 4),
            "status": "success",
            "details": {
                "model_type": type(model).__name__,
                "metric_name": _get_metric_name(task_id)
            }
        }
    
    except Exception as e:
        return {
            "score": 0,
            "status": "error",
            "error": f"Task {task_id} evaluation failed: {str(e)}"
        }


def _get_metric_name(task_id):
    """Get metric name for a given task ID"""
    metrics = {
        1: "R² Score",
        2: "Accuracy",
        3: "F1 Macro"
    }
    return metrics.get(task_id, "Unknown")
