"""
Utility functions for F1-Score Grand Prix
"""

import subprocess
import os
import uuid
import pandas as pd
import numpy as np
import platform
from pathlib import Path
from sklearn.preprocessing import StandardScaler, LabelEncoder

# ✅ Conditionally import 'resource' (Unix only)
if platform.system() != "Windows":
    import resource
else:
    resource = None


def load_task_info():
    """Return task descriptions and metadata"""
    return [
        {
            "id": 0,
            "name": "Data Preprocessing (EDA)",
            "description": "Clean and preprocess the training dataset. Remove nulls, normalize numeric features, encode categorical features. ",
            "function": "preprocess_data(df: pd.DataFrame) -> pd.DataFrame",
            "metric": "Automated checks (0-30 points)",
            "type": "eda"
        },
        {
            "id": 1,
            "name": "Regression",
            "description": "Build a model to predict continuous values (house prices, temperature, etc.).",
            "function": "train_model(X_train, y_train) + evaluate_model(model, X_test, y_test)",
            "metric": "R² Score (0-1)",
            "type": "regression"
        },
        {
            "id": 2,
            "name": "Binary Classification",
            "description": "Build a model to classify binary labels (yes/no, spam/not spam, etc.).",
            "function": "train_model(X_train, y_train) + evaluate_model(model, X_test, y_test)",
            "metric": "Accuracy (0-1)",
            "type": "classification_binary"
        },
        {
            "id": 3,
            "name": "Multi-class Classification",
            "description": "Build a model to classify multiple class labels (iris species, digit recognition, etc.).",
            "function": "train_model(X_train, y_train) + evaluate_model(model, X_test, y_test)",
            "metric": "F1 Macro (0-1)",
            "type": "classification_multiclass"
        }
    ]


def generate_submission_id():
    """Generate a unique submission ID"""
    return str(uuid.uuid4())[:8]


def safe_run_submission(script_path, args, timeout=120):
    """
    Run a Python script in a subprocess with optional resource limits.
    
    Args:
        script_path (Path): Path to submission script
        args (list): Arguments to pass to script
        timeout (int): Timeout in seconds
    
    Returns:
        CompletedProcess: Result of subprocess execution
    """
    try:
        # ✅ Use preexec_fn only on non-Windows systems
        run_kwargs = {
            "args": ["python", str(script_path)] + args,
            "capture_output": True,
            "text": True,
            "timeout": timeout
        }

        if platform.system() != "Windows":
            run_kwargs["preexec_fn"] = _set_resource_limits

        result = subprocess.run(**run_kwargs)
        return result
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Submission exceeded timeout ({timeout}s)")
    except Exception as e:
        raise RuntimeError(f"Failed to run submission: {str(e)}")


def _set_resource_limits():
    """
    Set resource limits for subprocess (Unix only).
    - Memory: 500 MB
    - CPU time: 120 seconds
    """
    if resource is None:
        # Windows does not support the resource module
        return

    try:
        # Limit virtual memory to 500 MB
        resource.setrlimit(resource.RLIMIT_AS, (500 * 1024 * 1024, 500 * 1024 * 1024))
        # Limit CPU time to 120 seconds
        resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
    except Exception:
        # Resource limits may not be available on all systems
        pass


def load_task_data(task_id, split="train"):
    """
    Load training or test data for a task.
    
    Args:
        task_id (int): Task ID (0-3)
        split (str): 'train' or 'test'
    
    Returns:
        pd.DataFrame: Loaded data
    """
    data_dir = Path(__file__).parent / "data"
    filepath = data_dir / f"task{task_id}_{split}.csv"
    
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")
    
    return pd.read_csv(filepath)


def compute_metrics(task_id, y_true, y_pred):
    """
    Compute evaluation metric based on task type.
    
    Args:
        task_id (int): Task ID (0-3)
        y_true: Ground truth labels
        y_pred: Predicted labels/values
    
    Returns:
        float: Computed metric score
    """
    from sklearn.metrics import r2_score, accuracy_score, f1_score
    
    if task_id == 1:
        # Regression: R² score
        return float(r2_score(y_true, y_pred))
    elif task_id == 2:
        # Binary classification: Accuracy
        return float(accuracy_score(y_true, y_pred))
    elif task_id == 3:
        # Multi-class classification: F1 macro
        return float(f1_score(y_true, y_pred, average='macro', zero_division=0))
    else:
        raise ValueError(f"Unknown task_id: {task_id}")


def validate_preprocessing(df_original, df_processed):
    """
    Validate preprocessed data (Task 0).
    
    Checks:
    - No null values
    - Numeric columns are standardized
    - Categorical columns are encoded
    
    Args:
        df_original: Original dataframe
        df_processed: Processed dataframe
    
    Returns:
        tuple: (score: int 0-30, details: dict)
    """
    score = 30
    details = {"checks_passed": []}
    
    # Check 1: No nulls (10 points)
    if df_processed.isnull().sum().sum() > 0:
        score -= 10
    else:
        details["checks_passed"].append("No null values")
    
    # Check 2: All columns are numeric (10 points)
    non_numeric = df_processed.select_dtypes(exclude=[np.number]).shape[1]
    if non_numeric > 0:
        score -= 10
    else:
        details["checks_passed"].append("All columns are numeric")
    
    # Check 3: Numeric columns are standardized (10 points)
    numeric_df = df_processed.select_dtypes(include=[np.number])
    means_ok = all(abs(numeric_df.mean()) < 0.5) and all(numeric_df.std() < 2)
    if not means_ok:
        score -= 5  # Partial credit
    else:
        details["checks_passed"].append("Numeric columns are standardized")
    
    return max(0, score), details
