import requests
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/predict")

st.set_page_config(page_title="Movie Hit/Flop Predictor", page_icon="🎬")

st.title("🎬 Movie Hit/Flop Predictor")
st.markdown("Fill in the movie detail to make prediction")

with st.form("prediction form"):
    title = st.text_input("Movie Title")
    overview = st.text_input("Overview")
    budget = st.number_input("Budget ($)", min_value=0, value=50000000)
    popularity = st.number_input("Popularity Score", min_value=0.0, value=100.0)
    vote_avg = st.slider("Vote Average", 0.0, 10.0, 7.0)
    submitted = st.form_submit_button("Predict")

if submitted:
    payload = {
        "title": title,
        "overview": overview,
        "budget": budget,
        "popularity": popularity,
        "vote_avg": vote_avg,
    }

    with st.spinner("Predicting..."):
        res = requests.post(API_URL, json=payload)
        data = res.json()

    pred = data["prediction"]
    confidence = data["confidence"]

    if pred == "Hit":
        st.success(f"🎯 **{pred}** — Confidence: {confidence}")
    else:
        st.error(f"💀 **{pred}** — Confidence: {confidence}")