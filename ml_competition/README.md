# F1-Score Grand Prix - ML Competition Platform

A clean, refactored ML competition platform with Flask backend and React frontend.

## Features

- **4 Tasks** (1 EDA + 3 ML)
  - Task 0: Data Preprocessing (automated checks)
  - Task 1: Regression (R² score)
  - Task 2: Classification (Accuracy)
  - Task 3: Multi-class Classification (F1 macro)
- **Safe Execution**: Submissions run in isolated subprocesses with CPU/memory/time limits
- **Live Leaderboard**: Real-time rankings for each task (top 20)
- **Submission Limit**: Max 3 submissions per team per task
- **JWT Authentication**: Optional login for team-based submissions

## Project Structure

```
ml_competition/
├── backend/                  # Flask backend
│   ├── app.py                # Flask app entry point
│   ├── config.py             # Configuration settings
│   ├── extensions.py         # Flask extensions (db, jwt, cors)
│   ├── routes/
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── tasks.py          # Task-related endpoints
│   │   ├── submissions.py    # Upload and evaluate endpoints
│   │   └── leaderboard.py    # Leaderboard endpoint
│   ├── evaluator.py          # Submission evaluation engine
│   ├── utils.py              # Helper functions
│   ├── database/
│   │   ├── models.py         # SQLAlchemy models
│   │   └── session.py        # Database utilities
│   ├── templates/            # ML starter templates
│   ├── data/                 # CSV datasets
│   ├── submissions/          # Stored .py uploads
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment variables template
│
├── frontend/                 # React + Tailwind frontend
│   ├── src/
│   │   ├── api/              # API client wrapper
│   │   ├── components/       # Reusable React components
│   │   ├── pages/            # Page components
│   │   ├── App.jsx           # Main app component
│   │   └── main.jsx          # Entry point
│   ├── public/
│   │   └── images/           # Static images
│   ├── index.html
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── package.json
│   └── .env.example          # Environment variables template
│
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or pnpm

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd ml_competition/backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env to set SECRET_KEY
   ```

5. **Run the backend**:
   ```bash
   python app.py
   ```

   Backend runs at: **http://localhost:8000**

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd ml_competition/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # VITE_API_BASE_URL=http://localhost:8000
   ```

4. **Run the frontend**:
   ```bash
   npm run dev
   ```

   Frontend runs at: **http://localhost:3000**

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | List all tasks with descriptions |
| GET | `/template/<task_id>` | Get starter template code |
| GET | `/sample-data/<task_id>` | Get sample data preview (100 rows) |
| GET | `/download/<task_id>` | Download training CSV |
| GET | `/leaderboard` | Fetch leaderboard JSON |

### Submission Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload/<task_id>` | Upload submission Python file |
| POST | `/evaluate/<submission_id>?task_id=...` | Evaluate submission |

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get JWT token |
| GET | `/auth/me` | Get current user info (requires auth) |

## Environment Variables

### Backend (.env)

```
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

### Frontend (.env)

```
VITE_API_BASE_URL=http://localhost:8000
```

## Submission Format

Participants must provide a Python file with one or more of these functions:

### Task 0 (EDA/Preprocessing)
```python
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    # Return cleaned dataframe
    pass
```

### Tasks 1-3 (Train & Evaluate)
```python
def train_model(X_train, y_train):
    # Return trained model object
    pass

def evaluate_model(model, X_test, y_test):
    # Return float score
    pass
```

## License

This project is provided as-is for educational purposes.
