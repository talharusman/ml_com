"""
Task 3: Multi-class Classification

Objective: Classify multiple class labels (e.g., iris species, digit recognition).

Your task:
1. Build a multi-class classification model using X_train and y_train
2. Evaluate your model on X_test and y_test
3. Return the F1 macro score

Example models to try:
- Logistic Regression
- Decision Tree Classifier
- Random Forest Classifier
- Gradient Boosting Classifier

Metric: F1 Macro Score (higher is better, max 1.0)
"""

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score


def train_model(X_train, y_train):
    """
    Train a multi-class classification model.
    
    Args:
        X_train: Training features
        y_train: Training multi-class labels (0, 1, 2, ...)
    
    Returns:
        Trained model object (must be picklable)
    """
    # TODO: Implement your model here
    model = LogisticRegression(max_iter=1000, multi_class='multinomial')
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    """
    Evaluate the trained model on test data.
    
    Args:
        model: Trained model object
        X_test: Test features
        y_test: Test multi-class labels (0, 1, 2, ...)
    
    Returns:
        float: F1 macro score (0-1)
    """
    # TODO: Implement your evaluation here
    y_pred = model.predict(X_test)
    score = f1_score(y_test, y_pred, average='macro', zero_division=0)
    return score
