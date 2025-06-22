import streamlit as st

# Streamlit multipage config
st.set_page_config(page_title="Unified Fraud Detection System", layout="wide")

# App header
st.title("🛡️ Unified Self-Learning Fraud Detection Platform")

# Intro description
st.markdown("""
Welcome to your AI-powered fraud detection system:
- Product Listing Fraud (Image + Text Embeddings)
- Buyer Transaction Fraud (Tabular XGBoost)
- Real-time self-learning with human feedback loop.
""")
