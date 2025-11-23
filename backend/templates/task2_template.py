"""
Task 2: Binary Classification

Objective: Classify binary labels (e.g., spam/not spam, fraud/not fraud).

Your task:
1. Build a classification model using X_train and y_train
2. Evaluate your model on X_test and y_test
3. Return the Accuracy score

Example models to try:
- Logistic Regression
- Decision Tree Classifier
- Random Forest Classifier
- Gradient Boosting Classifier

Metric: Accuracy (higher is better, max 1.0)
"""

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


def train_model(X_train, y_train):
    """
    Train a binary classification model.
    
    Args:
        X_train: Training features
        y_train: Training binary labels (0 or 1)
    
    Returns:
        Trained model object (must be picklable)
    """
    # TODO: Implement your model here
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    """
    Evaluate the trained model on test data.
    
    Args:
        model: Trained model object
        X_test: Test features
        y_test: Test binary labels (0 or 1)
    
    Returns:
        float: Accuracy score (0-1)
    """
    # TODO: Implement your evaluation here
    y_pred = model.predict(X_test)
    score = accuracy_score(y_test, y_pred)
    return score
