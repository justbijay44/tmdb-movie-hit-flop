import os
import joblib
import mlflow
import numpy as np
import scipy.sparse as sp
from fastapi import FastAPI
from pydantic import BaseModel
from src.utils.logger import logger

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Movie Hit/Flop Prediction")

tfidf = joblib.load("data/processed/tfidf.pkl")
scaler = joblib.load("data/processed/scaler.pkl")

def load_model():
    os.environ["MLFLOW_TRACKING_USERNAME"] = os.getenv("MLFLOW_TRACKING_USERNAME") or ""
    os.environ["MLFLOW_TRACKING_PASSWORD"] = os.getenv("MLFLOW_TRACKING_PASSWORD") or ""
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URL") or "")
    model = mlflow.sklearn.load_model("models:/movie-hit-flop-model/1")
    logger.info("Model loaded from registry")
    return model

model = load_model()

class MovieInput(BaseModel):
    title: str
    overview: str
    budget: float
    popularity: float
    vote_avg: float
    
@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.post("/predict")
def predict(movie: MovieInput):
    text = f"{movie.title} {movie.overview}"
    text_features = tfidf.transform([text])

    num_features = scaler.transform([[movie.vote_avg, movie.popularity, movie.budget]])
    num_sparse = sp.csr_matrix(num_features)

    X = sp.hstack([text_features, num_features])
    
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]

    result = "Hit" if pred == 1 else "Flop"
    confidence = round(float(max(proba)) * 100, 2) 

    logger.info(f"Prediction: {result} (Confidence: {confidence} for '{movie.title}')")

    return {
        "title": movie.title,
        "prediction": result,
        "confidence": confidence
    }