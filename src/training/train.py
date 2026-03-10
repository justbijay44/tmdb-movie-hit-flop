import os
import mlflow
import mlflow.sklearn
import numpy as np
import scipy.sparse as sp
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from src.utils.logger import logger
from dotenv import load_dotenv
load_dotenv()

# mlflow setup
def setup_mlflow():
    os.environ["MLFLOW_TRACKING_USERNAME"] = os.getenv("MLFLOW_TRACKING_USERNAME") or ""
    os.environ["MLFLOW_TRACKING_PASSWORD"] = os.getenv("MLFLOW_TRACKING_PASSWORD") or ""
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URL") or "")
    mlflow.set_experiment("movie-hit-flop-v2")

# load features
def load_features():
    X = sp.load_npz("data/processed/X.npz")
    y = np.load("data/processed/y.npy")
    return X, y

# train & log
def train(model, model_name, params, X_train, X_test, y_train, y_test):
    with mlflow.start_run(run_name=model_name):
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # metrics
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)   

        # log to mlflow
        mlflow.log_params(params)
        mlflow.log_metrics({
            "accuracy": float(accuracy), "f1": float(f1),
            "precision": float(precision), "recall": float(recall)
        })

        try:
            mlflow.sklearn.log_model(model, model_name) 
            logger.info(f"Model artifact saved: {model_name}")
        except Exception as e:
            logger.error(f"Failed to save model artifact: {e}")

        logger.info(f"{model_name} | accuracy_score: {accuracy:.2f} | f1_score: {f1:.2f}")

if __name__ == "__main__":
    setup_mlflow()
    X, y = load_features()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # experiment 1
    rf_params = {"n_estimators": 100, "max_depth":8}
    train(
        RandomForestClassifier(**rf_params, class_weight='balanced', random_state=42),  # type: ignore
        "RandomForest", rf_params, X_train, X_test, y_train, y_test
    )

    # experiment 2
    xgb_params = {"n_estimators": 100, "max_depth":6, "learning_rate": 0.1}
    train(
        XGBClassifier(**xgb_params, eval_metric="logloss", random_state=42),
        "XGBoost", xgb_params, X_train, X_test, y_train, y_test
    )

    # experiment 3 - rf tuned
    rf_params2 = {"n_estimators": 200, "max_depth": 15}
    train(
        RandomForestClassifier(**rf_params2, class_weight="balanced", random_state=42), # type: ignore
        "RandomForest_v2", rf_params2, X_train, X_test, y_train, y_test
    )

    # experiment 4 - xgb tuned
    xgb_params2 = {"n_estimators": 200, "max_depth": 8, "learning_rate": 0.05}
    train(
        XGBClassifier(**xgb_params2, eval_metric="logloss", random_state=42),
        "XGBoost_v2", xgb_params2, X_train, X_test, y_train, y_test
    )