import requests
import streamlit as st
from datetime import date
import os
from dotenv import load_dotenv
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/predict")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG = "https://image.tmdb.org/t/p/w300"

st.set_page_config(page_title="Movie Hit/Flop Predictor",
                   page_icon="🎬", layout="wide")

st.title("🎬 Movie Hit/Flop Predictor")

tab1, tab2 = st.tabs(["🔍 Search Movie", "🎯 Upcoming Movies"])

with tab1:
    st.subheader("Search a Movie")
    query = st.text_input("Enter a movie", placeholder="e.g. Oppenheimer")

    if query:
        res = requests.get(f"{TMDB_BASE}/search/movie?api_key={TMDB_API_KEY}&query={query}")
        results = res.json().get("results", [])

        if not results:
            st.warning("No movies found. Try a different name.")
        else:
            for movie in results[:5]:
                col1, col2 = st.columns([1, 4])
                with col1:
                    if movie.get("poster_path"):
                        st.image(f"{TMDB_IMG}{movie['poster_path']}", width=80)
                with col2:
                    st.write(f"**{movie['title']}** ({movie.get('release_date', 'N/A')[:4]})")
                    if st.button("Predict this", key=movie["id"]):
                        detail = requests.get(f"{TMDB_BASE}/movie/{movie['id']}?api_key={TMDB_API_KEY}").json()

                        payload = {
                            "title":      detail.get("title"),
                            "overview":   detail.get("overview", ""),
                            "budget":     detail.get("budget") or 50000000,
                            "popularity": detail.get("popularity", 50.0),
                            "vote_avg":   detail.get("vote_average", 7.0)
                        }

                        try:
                            pred_res = requests.post(API_URL, json=payload, timeout=60)
                            data = pred_res.json()
                            if data["prediction"] == "Hit":
                                st.success(f"🎯 **{data['prediction']}** — Confidence: {data['confidence']}")
                            else:
                                st.error(f"💀 **{data['prediction']}** — Confidence: {data['confidence']}")
                        except:
                            st.warning("⏳ API is waking up, please try again in 30 seconds.")

with tab2:
    st.subheader("🎯 Upcoming Movies")
    today = date.today().isoformat()

    upcoming = []
    for page in range(1, 8):
        res = requests.get(f"{TMDB_BASE}/movie/upcoming?api_key={TMDB_API_KEY}&page={page}")
        upcoming.extend(res.json().get("results", []))

    upcoming = [m for m in upcoming if m.get("release_date", "") >= today]
    upcoming = sorted(upcoming, key=lambda m: m.get("release_date", ""))
    if not upcoming:
        res = requests.get(f"{TMDB_BASE}/movie/now_playing?api_key={TMDB_API_KEY}&page=1")
        upcoming = res.json().get("results", [])
        st.caption("Showing currently playing movies.")

    cols = st.columns(4)
    for i, movie in enumerate(upcoming[:12]):
        with cols[i % 4]:
            if movie.get('poster_path'):
                st.image(f"{TMDB_IMG}{movie['poster_path']}", width="stretch")
            st.write(f"**{movie['title']}**")
            st.caption(f"Release: {movie.get('release_date', 'TBA')}")

            if st.button("Prediction", key=f"upcoming_{movie['id']}"):
                detail = requests.get(f"{TMDB_BASE}/movie/{movie['id']}?api_key={TMDB_API_KEY}").json()

                payload = {
                    "title":      detail.get("title"),
                    "overview":   detail.get("overview", ""),
                    "budget":     detail.get("budget") or 50000000,
                    "popularity": detail.get("popularity", 50.0),
                    "vote_avg":   detail.get("vote_average", 7.0)
                }

                try:
                    pred_res = requests.post(API_URL, json=payload, timeout=60)
                    data = pred_res.json()
                    if data["prediction"] == "Hit":
                        st.success(f"🎯 **Hit** — Confidence: {data['confidence']}")
                    else:
                        st.error(f"💀 **Flop** — Confidence: {data['confidence']}")
                except:
                    st.warning("⏳ API is waking up, please try again in 30 seconds.")