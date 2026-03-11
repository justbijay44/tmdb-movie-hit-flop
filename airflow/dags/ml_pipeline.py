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

    _= task_ingest() >> task_export() >> task_features()

movie_ml_pipeline()