import os
import pandas as pd
from src.ingestion.fetch_movies import get_db_connection

def export_to_csv():
    conn = get_db_connection()
    query = "SELECT * FROM movies WHERE budget > 0 AND revenue > 0;"
    df = pd.read_sql_query(query, conn)   
    conn.close()

    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/movies.csv", index=False)
    print(f"Exported {len(df)} rows to data/raw/movies.csv")

if __name__ == "__main__":
    export_to_csv()