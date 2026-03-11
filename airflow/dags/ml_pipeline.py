from airflow.sdk import dag, task
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/opt/airflow')

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

@dag(
    dag_id="movie_ml_pipeline",
    default_args=default_args,
    schedule="@weekly",
    catchup=False,
    description="End-to-End ML pipeline for movies hit/flop prediction",
)

def movie_ml_pipeline():
    @task
    def task_ingest():
        from src.ingestion.fetch_movies import (get_db_connection, create_table,
                                                 fetch_movies, insert_movies)

        conn = get_db_connection()
        create_table(conn)
        movies = fetch_movies(pages=10)
        insert_movies(conn, movies)
        conn.close()

    @task
    def task_export():
        from src.ingestion.export_data import export_to_csv
        export_to_csv()

    @task
    def task_features():
        from src.features.build_features import (load_data, create_labels,
                                                build_features, save_feature)

        df = load_data()
        df = create_labels(df)
        X, y, tfidf, scaler = build_features(df)
        save_feature(X, y, tfidf, scaler)

    @task
    def task_train():
        from src.training.train import setup_mlflow, load_features, train
        from sklearn.ensemble import RandomForestClassifier
        from xgboost import XGBClassifier
        from sklearn.model_selection import train_test_split
        
        setup_mlflow()
        X, y = load_features()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        rf_params = {"n_estimators":100, "max_depth": 8}
        train(
            RandomForestClassifier(**rf_params, class_weight="balanced", random_state=42),  # type: ignore
            "RandomForest", rf_params, X_train, X_test, y_train, y_test
        )

        xgb_params = {"n_estimators": 100, "max_depth": 6, "learning_rate": 0.1}
        train(
            XGBClassifier(**xgb_params, eval_metric="logloss", random_state=42),
            "XGBoost", xgb_params, X_train, X_test, y_train, y_test
        )

    @task
    def task_register():
        from src.training.register_model import register_best_model
        register_best_model()

    _= task_ingest() >> task_export() >> task_features() >> task_train() >> task_register()

movie_ml_pipeline()