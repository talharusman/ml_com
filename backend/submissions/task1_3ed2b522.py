"""
Task 1: Regression

Objective: Predict continuous values (e.g., house prices, temperature).

Your task:
1. Build a regression model using X_train and y_train
2. Evaluate your model on X_test and y_test
3. Return the RÂ² score

Example models to try:
- Linear Regression
- Decision Tree Regressor
- Random Forest Regressor
- Gradient Boosting Regressor

Metric: RÂ² Score (higher is better, max 1.0)
"""

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def train_model(X_train, y_train):
    """
    Train a regression model.
    
    Args:
        X_train: Training features
        y_train: Training target values
    
    Returns:
        Trained model object (must be picklable)
    """
    # TODO: Implement your model here
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    """
    Evaluate the trained model on test data.
    
    Args:
        model: Trained model object
        X_test: Test features
        y_test: Test target values
    
    Returns:
        float: RÂ² score (0-1)
    """
    # TODO: Implement your evaluation here
    y_pred = model.predict(X_test)
    score = r2_score(y_test, y_pred)
    return score
