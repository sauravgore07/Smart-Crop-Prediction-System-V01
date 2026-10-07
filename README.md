# CropPredict

Smart crop recommendation system with ML predictions, market prices, and user farm management.

## Stack
- **Frontend**: React + Vite + TailwindCSS + Leaflet
- **Backend**: FastAPI + SQLite + SQLAlchemy
- **ML**: scikit-learn RandomForest

## Quick Start

### 1. Train the ML model (one-time)
```bash
# Download dataset from Kaggle first:
# https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset
# Place it at ml_training/Crop_recommendation.csv

pip install scikit-learn pandas numpy
python ml_training/train_model.py
```

### 2. Start the backend
```bash
cd backend
python -m venv venv
deactivate

source venv/bin/activate      # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# API docs → http://localhost:8000/docs
```

### 3. Start the frontend
```bash
cd frontend
npm install
npm run dev
# App → http://localhost:5173
```

## Environment Variables
Copy `.env` and fill in your values. The defaults work for local development.

## Project Structure
```
croppredict/
├── frontend/          React app
├── backend/           FastAPI server + SQLite DB
├── ml_training/       Model training scripts
└── alembic/           DB migrations
```
