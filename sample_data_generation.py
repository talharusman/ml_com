"""
Generate synthetic datasets for F1-Score Grand Prix tasks
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.datasets import make_regression, make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Set random seed for reproducibility
np.random.seed(42)

# Output directory
DATA_DIR = Path(__file__).parent / "backend" / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)


def generate_task0_data():
    """
    Generate Task 0 (EDA/Preprocessing) dataset.
    Small dataset with missing values, mixed data types, and non-normalized features.
    """
    n_samples = 500
    
    # Create synthetic data with various issues
    data = {
        'age': np.random.randint(18, 80, n_samples),
        'salary': np.random.randint(30000, 150000, n_samples),
        'years_experience': np.random.randint(0, 40, n_samples),
        'department': np.random.choice(['HR', 'Engineering', 'Sales', 'Marketing'], n_samples),
        'is_manager': np.random.choice([0, 1], n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Add some missing values
    df.loc[np.random.choice(df.index, 20), 'salary'] = np.nan
    df.loc[np.random.choice(df.index, 15), 'years_experience'] = np.nan
    
    # Save training data (with nulls)
    df.to_csv(DATA_DIR / "task0_train.csv", index=False)
    print(f"✓ Generated task0_train.csv ({len(df)} rows)")
    
    # Save test data (similar structure)
    df_test = df.iloc[:50].copy()
    df_test.to_csv(DATA_DIR / "task0_test.csv", index=False)
    print(f"✓ Generated task0_test.csv ({len(df_test)} rows)")


def generate_task1_data():
    """
    Generate Task 1 (Regression) dataset.
    Predicting continuous values (house prices).
    """
    n_samples = 1000
    n_features = 10
    
    # Generate regression dataset
    X, y = make_regression(n_samples=n_samples, n_features=n_features, noise=20, random_state=42)
    
    # Create dataframe with feature names
    df_X = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(n_features)])
    df_X['target'] = y
    
    # Split into train and test
    df_train, df_test = train_test_split(df_X, test_size=0.3, random_state=42)
    
    df_train.to_csv(DATA_DIR / "task1_train.csv", index=False)
    df_test.to_csv(DATA_DIR / "task1_test.csv", index=False)
    
    print(f"✓ Generated task1_train.csv ({len(df_train)} rows)")
    print(f"✓ Generated task1_test.csv ({len(df_test)} rows)")


def generate_task2_data():
    """
    Generate Task 2 (Binary Classification) dataset.
    Predicting binary labels (e.g., spam/not spam).
    """
    n_samples = 1000
    n_features = 10
    
    # Generate binary classification dataset
    X, y = make_classification(n_samples=n_samples, n_features=n_features, n_classes=2, 
                               n_informative=8, n_redundant=2, random_state=42)
    
    # Create dataframe
    df_X = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(n_features)])
    df_X['target'] = y
    
    # Split into train and test
    df_train, df_test = train_test_split(df_X, test_size=0.3, random_state=42)
    
    df_train.to_csv(DATA_DIR / "task2_train.csv", index=False)
    df_test.to_csv(DATA_DIR / "task2_test.csv", index=False)
    
    print(f"✓ Generated task2_train.csv ({len(df_train)} rows)")
    print(f"✓ Generated task2_test.csv ({len(df_test)} rows)")


def generate_task3_data():
    """
    Generate Task 3 (Multi-class Classification) dataset.
    Predicting multiple class labels (e.g., iris species, digit recognition).
    """
    n_samples = 1200
    n_features = 10
    n_classes = 4
    
    # Generate multi-class classification dataset
    X, y = make_classification(n_samples=n_samples, n_features=n_features, n_classes=n_classes,
                               n_informative=8, n_redundant=2, n_clusters_per_class=1, 
                               random_state=42)
    
    # Create dataframe
    df_X = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(n_features)])
    df_X['target'] = y
    
    # Split into train and test
    df_train, df_test = train_test_split(df_X, test_size=0.3, random_state=42)
    
    df_train.to_csv(DATA_DIR / "task1_train.csv", index=False)
    df_test.to_csv(DATA_DIR / "task3_test.csv", index=False)
    
    print(f"✓ Generated task3_train.csv ({len(df_train)} rows)")
    print(f"✓ Generated task3_test.csv ({len(df_test)} rows)")


if __name__ == "__main__":
    print("Generating synthetic datasets for F1-Score Grand Prix...\n")
    
    generate_task0_data()
    print()
    generate_task1_data()
    print()
    generate_task2_data()
    print()
    generate_task3_data()
    
    print("\n✓ All datasets generated successfully!")
    print(f"  Location: {DATA_DIR}")
