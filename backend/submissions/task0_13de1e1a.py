"""
Task 0: Data Preprocessing (EDA)

Objective: Clean and preprocess the training dataset.

Your task:
1. Remove/handle null values
2. Normalize numeric features (standardization)
3. Encode categorical features
4. Return the cleaned dataframe

Evaluation:
- No null values: +10 points
- All columns numeric: +10 points
- Proper normalization: +10 points
- Total: 30 points
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess the input dataframe.
    
    Args:
        df (pd.DataFrame): Raw input data
    
    Returns:
        pd.DataFrame: Cleaned and preprocessed data
    """
    df = df.copy()
    
    # Handle missing values
    # TODO: Fill or drop null values
    df = df.dropna()  # Simple approach: drop rows with nulls
    
    # Encode categorical columns
    # TODO: Encode categorical features
    categorical_cols = df.select_dtypes(include=['object']).columns
    le_dict = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        le_dict[col] = le
    
    # Normalize numeric columns
    # TODO: Standardize numeric features
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    
    return df
