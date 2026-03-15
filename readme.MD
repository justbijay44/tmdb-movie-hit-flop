## TMDB Movie Hit or Flop prediction

A MLOPs based system to predict whether an upcoming movie will be a hit or a flop

### Tech Stack

1. Ingestion - Python, TMDB API, PostgreSQL
2. Versioning - DVC, Dagshub
3. Feature Engineering - Pandas, Scikit-learn, TF-IDF
4. Experiment - Mlflow, Dagshub, RandomForest, XGBoost
5. Serving - FASTAPI, Streamlit
6. Orchestration - Airflow
7. Containerization - Docker, Docker Compose

### To start all services

- docker-compose up or docker-compose up -d

This will start containers for postgres, airflow, fastapi, streamlit.

### Trigger the pipeline

1. Go to: http://localhost:8080 
2. On dags find movie_ml_pipeline 
3. Click on trigger Dag
4. Watch the pipeline to see the orchestration part and the pipeline successed

### Make Prediction

1. Streamlit UI: http://localhost:8501
2. APIDocs: http://localhost:8000/docs

** Note **

For now the user has to pass on the following values to get a prediction

{
    "title": "Oppenheimer",
    "overview": "The story of J. Robert Oppenheimer and the development of the atomic bomb",
    "budget": 100000000,
    "popularity": 150.0,
    "vote_avg": 8.5
}


### Deployment

We have performed deployment through render and as its from free tier. The site will be inactive after 15 minutes of not in use.

FastAPI url - https://tmdb-movie-hit-flop.onrender.com/docs
Streamlit url - https://tmdb-movie-hit-flop-1.onrender.com/

The fastapi has to be active before using the streamlit.