import mlflow
from src.training.train import setup_mlflow
from src.utils.logger import logger

def register_best_model():
    setup_mlflow()

    runs = mlflow.search_runs(
        experiment_names=["movie-hit-flop-v2"],
        order_by=["metrics.f1 DESC"]
    )

    best_run = runs.iloc[0] # type: ignore
    run_id = best_run["run_id"] 
    f1 = best_run["metrics.f1"]
    run_name = best_run["tags.mlflow.runName"]

    logger.info(f"Best run_id={run_id} with f1_score: {f1}")

    model_uri = f"runs:/{run_id}/{run_name}"
    mv = mlflow.register_model(model_uri, "movie-hit-flop-model")

    logger.info(f"Model Registered, version={mv.version}")

if __name__ == "__main__":
    register_best_model()