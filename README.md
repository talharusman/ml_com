# F1-Score Grand Prix - Local ML Competition Platform

A lightweight, locally-runnable ML competition platform that allows participants to compete on multiple tasks by submitting Python code. Submissions are evaluated against hidden test data with automatic metric computation.

## Features

- **4 Tasks** (1 EDA + 3 ML)
  - Task 0: Data Preprocessing (automated checks)
  - Task 1: Regression (R² score)
  - Task 2: Classification (Accuracy)
  - Task 3: Multi-class Classification (F1 macro)
- **Safe Execution**: Submissions run in isolated subprocesses with CPU/memory/time limits
- **Live Leaderboard**: Real-time rankings for each task
- **Simple Web UI**: Download training data, upload submissions, view results

## Quick Start

### Requirements
- Python 3.10+
- pip or conda

### Local Installation

1. **Clone/extract the project**:
\`\`\`bash
cd f1_score_grand_prix
\`\`\`

2. **Install dependencies**:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. **Run the backend**:
\`\`\`bash
python backend/main.py
\`\`\`

4. **Open your browser**:
\`\`\`
http://localhost:8000
\`\`\`

## Project Structure

\`\`\`
f1_score_grand_prix/
├── README.md
├── requirements.txt
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── evaluator.py            # Submission evaluation engine
│   ├── utils.py                # Helper functions (metrics, data loading, sandboxing)
│   ├── data/
│   │   ├── task0_train.csv     # EDA training data
│   │   ├── task0_test.csv      # EDA test data (hidden)
│   │   ├── task1_train.csv     # Regression training data
│   │   ├── task1_test.csv      # Regression test data (hidden)
│   │   ├── task2_train.csv     # Classification training data
│   │   ├── task2_test.csv      # Classification test data (hidden)
│   │   ├── task3_train.csv     # Multi-class training data
│   │   └── task3_test.csv      # Multi-class test data (hidden)
│   ├── submissions/            # Uploaded submissions (auto-created)
│   ├── templates/              # Submission templates
│   │   ├── task0_template.py
│   │   ├── task1_template.py
│   │   ├── task2_template.py
│   │   └── task3_template.py
│   ├── leaderboard.json        # Persistent leaderboard
│   └── static/                 # Frontend files
│       ├── index.html
│       ├── styles.css
│       └── upload.js
├── sample_data_generation.py  # Script to generate synthetic datasets
├── docker/
│   └── runner.Dockerfile      # Optional Docker-based sandboxing
└── run_local.sh               # Setup and run script
\`\`\`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve frontend (index.html) |
| GET | `/tasks` | List all tasks with descriptions |
| GET | `/download/{task_id}` | Download training CSV |
| POST | `/upload/{task_id}` | Upload submission Python file |
| POST | `/evaluate/{submission_id}` | Evaluate submission |
| GET | `/leaderboard` | Fetch leaderboard JSON |

## Submission Format

Participants must provide a Python file (`submission.py`) with one or more of these functions:

### Task 0 (EDA/Preprocessing)
\`\`\`python
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    # Return cleaned dataframe
    pass
\`\`\`

### Tasks 1-3 (Train & Evaluate)
\`\`\`python
def train_model(X_train, y_train):
    # Return trained model object (must be picklable)
    pass

def evaluate_model(model, X_test, y_test):
    # Return float score
    pass
\`\`\`

## Sandboxing & Security

### Local Execution (subprocess + resource limits)
Submissions run in isolated subprocesses with:
- **Time limit**: 120 seconds per submission
- **Memory limit**: 500 MB
- **CPU time limit**: enforced via `resource.setrlimit()`

The evaluator uses Python's `subprocess` module with the `resource` module to enforce limits at process creation.

### Production / Docker (optional)
For stricter isolation, use the provided `docker/runner.Dockerfile`:

\`\`\`bash
docker build -f docker/runner.Dockerfile -t ml-runner .
docker run --rm --memory=512m --cpus=1 -v $(pwd)/submissions:/submissions ml-runner python /submissions/task1_team_xyz.py --run
\`\`\`

## Evaluation Pipeline

1. User uploads `submission.py` to `/upload/{task_id}`
2. Backend saves submission and generates a unique `submission_id`
3. User clicks "Evaluate" or backend auto-evaluates
4. Evaluator:
   - Runs submission in a sandboxed subprocess
   - Loads training/test data
   - Calls `train_model()` and `evaluate_model()` (or `preprocess_data()` for Task 0)
   - Computes metric (R², Accuracy, F1, or preprocessing checks)
   - Returns score and updates leaderboard
5. Leaderboard is updated in real-time and persisted to `leaderboard.json`

## Task Descriptions

### Task 0: Data Preprocessing (EDA)
**Goal**: Clean and preprocess the training data.

Evaluation checks:
- No null values in output
- Numeric columns are standardized (mean ≈ 0, std ≈ 1)
- Categorical columns are encoded
- Output data types are consistent

**Score**: 0-30 points based on automated checks

### Task 1: Regression
**Goal**: Build a model to predict continuous values.

**Metric**: R² score (0 = constant prediction, 1 = perfect fit)

### Task 2: Binary Classification
**Goal**: Build a model to predict binary labels.

**Metric**: Accuracy (0 to 1)

### Task 3: Multi-class Classification
**Goal**: Build a model to predict multiple class labels.

**Metric**: F1 macro-average (0 to 1)

## Data Generation

To generate larger synthetic datasets (10k–20k rows):

\`\`\`bash
python sample_data_generation.py
\`\`\`

This overwrites the `backend/data/task*_train.csv` files with larger datasets.

## Troubleshooting

**Port already in use**: Change port in `backend/main.py` (default: 8000)
\`\`\`python
uvicorn.run(app, host="0.0.0.0", port=9000)
\`\`\`

**Timeout errors**: Increase timeout in `backend/evaluator.py` (default: 120s)

**Memory/CPU limit issues**: Adjust in `backend/utils.py` (`safe_run_submission()`)

## License

This project is provided as-is for educational purposes.
