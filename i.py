import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("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")
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer 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"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

st.set_page_config(page_title="Smart Summarizer", layout="centered")

st.markdown("""
    <style>
        .main {
            background-color: #0e1117;
            color: white;
        }
        .stTextArea, .stButton {
            margin-top: 1.5rem;
        }
        .summary-box {
            background-color: #1f2937;
            padding: 1rem;
            border-radius: 10px;
            margin-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>📝 Smart AI Summarizer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Give me a wall of text, and I’ll break it down for you ✂️</p>", unsafe_allow_html=True)

text = st.text_area("Paste your long paragraph below", height=220)

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    generate = st.button("✨ Generate Summary")

if generate:
    if not text.strip():
        st.warning("Please add some content to summarize.")
    else:
        with st.spinner("Crunching the text..."):
            result = query({"inputs": text})
            try:
                summary = result[0]["summary_text"]
                st.markdown("<div class='summary-box'><h4>📌 Summary:</h4><p>{}</p></div>".format(summary), unsafe_allow_html=True)
            except:
                st.error("Oops! Couldn’t process the summary.")
                st.json(result)
