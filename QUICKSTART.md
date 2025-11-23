# F1-Score Grand Prix - Quick Start Guide

## Installation

### Option 1: Bash Script (Recommended)

\`\`\`bash
chmod +x run_local.sh
./run_local.sh
\`\`\`

This will:
1. Check Python version
2. Install dependencies
3. Generate sample datasets
4. Start the backend server

### Option 2: Manual Steps

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Generate sample data
python3 sample_data_generation.py

# Run the backend
python3 backend/main.py
\`\`\`

## Accessing the Platform

Open your browser and navigate to:
\`\`\`
http://localhost:8000
\`\`\`

## Submitting a Solution

### Step 1: Download Template
1. Click on a task (Task 0, 1, 2, or 3)
2. Click "📥 Download Template"
3. Edit the template with your solution

### Step 2: Submit
1. Click "📤 Submit" on the task
2. Select your solution file (`.py` extension)
3. Click "Submit"

### Step 3: View Results
- Results appear immediately on the leaderboard
- Refresh the page or wait for auto-refresh (every 5 seconds)
- Check your score and rank

## Task Overview

### Task 0: Data Preprocessing (30 points)
**Function**: `preprocess_data(df: pd.DataFrame) -> pd.DataFrame`

Implement data cleaning:
- Remove null values
- Normalize numeric features
- Encode categorical features

**Scoring**:
- No nulls: +10 points
- All numeric: +10 points
- Standardization: +10 points

### Task 1: Regression (R² Score)
**Functions**:
\`\`\`python
def train_model(X_train, y_train):
    # Return trained model
    pass

def evaluate_model(model, X_test, y_test):
    # Return R² score (0-1)
    pass
\`\`\`

Build a model to predict continuous values.

**Example**:
\`\`\`python
from sklearn.linear_model import LinearRegression

def train_model(X_train, y_train):
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    return model.score(X_test, y_test)
\`\`\`

### Task 2: Binary Classification (Accuracy)
**Functions**: Same as Task 1, but returns Accuracy

Build a model to classify binary labels (0/1).

**Example**:
\`\`\`python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def train_model(X_train, y_train):
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    return accuracy_score(y_test, model.predict(X_test))
\`\`\`

### Task 3: Multi-class Classification (F1 Macro)
**Functions**: Same as Task 1, but returns F1 macro score

Build a model to classify multiple class labels (0, 1, 2, 3, ...).

**Example**:
\`\`\`python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import f1_score

def train_model(X_train, y_train):
    model = GradientBoostingClassifier()
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    return f1_score(y_test, model.predict(X_test), average='macro')
\`\`\`

## Troubleshooting

### Port Already in Use
If port 8000 is already in use:

\`\`\`bash
# Option 1: Use a different port
python3 -c "
import sys; sys.path.insert(0, 'backend')
from main import app
import uvicorn
uvicorn.run(app, host='0.0.0.0', port=9000)
"
\`\`\`

### Import Errors
Ensure all dependencies are installed:
\`\`\`bash
pip install -r requirements.txt --upgrade
\`\`\`

### Submission Timeout
Submissions have a 120-second timeout by default. To increase:

Edit `backend/utils.py`:
\`\`\`python
def safe_run_submission(script_path, args, timeout=180):  # Change 120 to 180
    ...
\`\`\`

### Memory Issues
Adjust memory limit in `backend/utils.py`:
\`\`\`python
def _set_resource_limits():
    # Change 500 * 1024 * 1024 to desired bytes (e.g., 1 GB = 1024 * 1024 * 1024)
    resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 1024, 1024 * 1024 * 1024))
\`\`\`

## FAQ

### Can I use external libraries?
Yes! As long as they're installed in `requirements.txt`. Contact the organizer to add new libraries.

### Is my code secure?
Yes. Submissions run in isolated subprocesses with resource limits (CPU time, memory).

### How are ties broken?
Submissions are ranked by score (highest first), then by timestamp (earliest first).

### Can I submit multiple times?
Yes! Each submission is evaluated independently. Only your best score counts for ranking.

## Support

For issues or questions, check the `README.md` or contact the competition organizers.

Happy competing!
