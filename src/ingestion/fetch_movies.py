import os
import time
import requests
import psycopg2
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
load_dotenv()

# get connection to postgres
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
        # sslmode="disable"
    )

# create table
def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS movies(
                id              INTEGER PRIMARY KEY,
                title           TEXT,
                overview        TEXT,
                genres          TEXT,
                vote_avg        FLOAT,
                release_date    TEXT,
                popularity      FLOAT,
                budget          BIGINT,
                revenue         BIGINT
            )
        """)
        conn.commit()

# fetch detail of a movie
def fetch_movie_detail(movie_id):
    api = os.getenv("TMDB_API_KEY")
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api}"
    res = requests.get(url)
    data = res.json()
    return {
        "budget": data.get("budget", 0),
        "revenue": data.get("revenue", 0)
    }

# fetch from tmdb
def fetch_movies(pages=5):
    api = os.getenv("TMDB_API_KEY")
    raw = []
    for page in range(1, pages+1):
        endpoints=["popular", "top_rated"]
        for endpoint in endpoints:
            url = f"https://api.themoviedb.org/3/movie/{endpoint}?api_key={api}&page={page}"
            res = requests.get(url)
            data = res.json()
            raw.extend(data["results"])

    # to fetch detail in parallel
    def enrich(m):
        detail = fetch_movie_detail(m["id"])
        # time.sleep(0.5)
        return {
            "id":               m.get("id"),
            "title":            m.get("title"),
            "overview":         m.get("overview"),
            "genres":           str(m.get("genre_ids")),
            "vote_avg":         m.get("vote_average"),
            "release_date":     m.get("release_date"),
            "popularity":       m.get("popularity"),
            "budget":           detail["budget"], 
            "revenue":          detail["revenue"],
        }

    with ThreadPoolExecutor(max_workers=10) as executor:
        movies = list(executor.map(enrich, raw))

    return movies

# insert into db
def insert_movies(conn, movies):
    with conn.cursor() as cur:
        for movie in movies:
            cur.execute("""
                INSERT INTO movies (id, title, overview, genres, vote_avg, release_date, popularity, budget, revenue)  
                VALUES (%(id)s, %(title)s, %(overview)s, %(genres)s, %(vote_avg)s, %(release_date)s, %(popularity)s, %(budget)s, %(revenue)s)
                ON CONFLICT (id) DO NOTHING       
            """, movie)
        conn.commit()
    print(f"Inserted {len(movies)} movies.")

if __name__ == "__main__":
    conn = get_db_connection()
    create_table(conn)
    movies = fetch_movies(pages=50)
    insert_movies(conn, movies)
    conn.close()