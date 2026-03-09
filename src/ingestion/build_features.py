import os
import re
import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer

from src.utils.logger import logger

def load_data():
    df = pd.read_csv("data/raw/movies.csv")
    return df

def create_labels(df):
    df["label"] = ((df['revenue'] > 2.5 * df['budget']) & (df['vote_avg'] >= 7.5)).astype(int)
    return df

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[^a-z0-9\s]', '', text.lower().strip())
    return text

def build_features(df):
    df["clean_text"] = df.apply(lambda x: clean_text(x["title"]) + " " + clean_text(x["overview"]), axis=1)
    tfidf = TfidfVectorizer(max_features=100, stop_words="english")
    text_features = tfidf.fit_transform(df["clean_text"])

    num_cols = ['vote_avg', 'popularity', 'budget']
    scaler = MinMaxScaler()
    num_features = scaler.fit_transform(df[num_cols])

    num_sparse = sp.csr_matrix(num_features)
    X = sp.hstack([text_features, num_sparse])
    y = df["label"].values
    return X, y, tfidf, scaler

def save_feature(X, y):
    os.makedirs("data/processed", exist_ok=True)
    sp.save_npz("data/processed/X.npz", X)
    np.save("data/processed/y.npy", y)
    logger.info(f"Saved features: X={X.shape}, y={y.shape}")

if __name__ == "__main__":
    df = load_data()
    df = create_labels(df)
    X, y, tfidif, scaler = build_features(df)
    save_feature(X, y)