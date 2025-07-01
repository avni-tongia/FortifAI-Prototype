
import streamlit as st
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Load models
text_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
resnet = models.resnet152(pretrained=True)
resnet.eval()
resnet = torch.nn.Sequential(*(list(resnet.children())[:-1]))

transform_pipeline = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def get_image_embedding(image_bytes):
    image = Image.open(image_bytes).convert('RGB')
    tensor = transform_pipeline(image).unsqueeze(0)
    with torch.no_grad():
        embedding = resnet(tensor).squeeze().numpy()
    return embedding.flatten()

def get_text_embedding(text):
    return text_model.encode([text])[0]

def get_price_anomaly_score(price, brand, stats_df):
    group_key = brand
    group_stats = stats_df[stats_df['group_key'] == group_key]
    if not group_stats.empty:
        mean = group_stats['rolling_mean'].values[0]
        std = group_stats['rolling_std'].values[0]
        if std > 0:
            z_score = abs((price - mean) / std)
        else:
            z_score = 0.0
        # Manually scale Z-score to [0, 1] using an upper cap
        scaled_score = min(z_score / 3.0, 1.0)

        return scaled_score, z_score, mean, std
    return 0.0, 0.0, None, None

try:
    legit_text_pool = pickle.load(open('legit_text_pool.pkl', 'rb'))
    fraud_text_pool = pickle.load(open('fraud_text_pool.pkl', 'rb'))
    legit_image_embeddings = np.load('legit_image_embeddings.npy')
    price_stats_df = pd.read_csv('price_stats.csv')
except:
    st.error("Required files not found. Please ensure embeddings and stats files are in place.")
    st.stop()

st.set_page_config(page_title="Product Fraud Detection", layout="wide")
st.title("🛡️ Product Listing Fraud Detection System")

# Split into left and right columns
left_col, right_col = st.columns([1, 2.2])

# Top row: aligned labels
with left_col:
    st.markdown("<div style='padding-top:8px; font-size:16px;'> Upload Product Image</div>", unsafe_allow_html=True)
with right_col:
    st.markdown("**Product Title / Description**")

# Second row: uploader and input
with left_col:
    uploaded_file = st.file_uploader("", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")

with right_col:
    product_text = st.text_area("", height=90, label_visibility="collapsed")

    # Bottom row: price and brand
    col1, col2 = st.columns(2)
    with col1:
        product_price = st.number_input("Price (USD)", min_value=0.0, format="%.2f")
    with col2:
        brand = st.text_input("Brand Name")


if uploaded_file and product_text and product_price and brand:
    image_embedding = get_image_embedding(uploaded_file)
    text_embedding = get_text_embedding(product_text)

    text_legit_sim = cosine_similarity([text_embedding], legit_text_pool).max()
    text_fraud_sim = cosine_similarity([text_embedding], fraud_text_pool).max()
    text_score = max(0, text_fraud_sim - text_legit_sim)

    image_sim = cosine_similarity([image_embedding], legit_image_embeddings).max()
    image_score = 1 - image_sim

    price_score, z_score_price, mean_price, std_price = get_price_anomaly_score(product_price, brand, price_stats_df)

    final_score = max(text_score, price_score, image_score)

    if final_score >= 0.75:
        risk_level = "High Risk"
    elif final_score >= 0.4:
        risk_level = "Moderate Risk"
    else:
        risk_level = "Low Risk"

    st.markdown(
    f"<h3 style='text-align: center;'> Fraud Risk Score: <span style='color:#FF4B4B'>{final_score:.2f}</span> — {risk_level}</h3>",
    unsafe_allow_html=True)

    left, right = st.columns([1, 1], gap="small")

    with left:
        if mean_price is not None:
            st.markdown("""
                <div style='
                    background-color:#ffffff;
                    color:#000000;
                    padding: 16px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.08);
                    font-size: 15px;
                    line-height: 1.6;
                    margin-bottom: 0px;
                '>
                    <strong style='font-size: 25px;'> Price Anomaly Explanation</strong><br>
                    • Mean price for <b>{brand}</b>: ₹{mean_price:.2f}<br>
                    • Std deviation: ₹{std_price:.2f}<br>
                    • Z-score: {z_score_price:.2f}<br>
                    • Your price: ₹{product_price:.2f}
                </div>
            """.format(
                brand=brand.upper(),
                mean_price=mean_price,
                std_price=std_price,
                z_score_price=z_score_price,
                product_price=product_price
            ), unsafe_allow_html=True)

    with right:
        st.markdown("#### Contribution Breakdown")
        labels = ['Text', 'Image', 'Price']
        scores = [text_score, image_score, price_score]
        fig, ax = plt.subplots(figsize=(1.8, 1.8))
        bars = ax.barh(labels, scores, color=['#F39C12', '#3498DB', '#E74C3C'])
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.01, bar.get_y() + bar.get_height() / 2,
                    f"{width:.2f}", va='center', fontsize=8)
        ax.set_xlim(0, 1)
        ax.set_title("Fraud Risk Contribution", fontsize=9)
        ax.tick_params(axis='y', labelsize=8)
        ax.tick_params(axis='x', labelsize=8)
        st.pyplot(fig)


    st.markdown("#### 📝 Moderator Feedback")
    feedback = st.radio("Is this prediction correct?", ["Correct (Fraud)", "Incorrect (Legit)"])
    if st.button("Submit Feedback"):
        log_data = {
            "timestamp": datetime.datetime.now(),
            "description": product_text,
            "price": product_price,
            "brand": brand,
            "text_score": text_score,
            "image_score": image_score,
            "price_score": price_score,
            "z_score_price": z_score_price,
            "mean_price": mean_price,
            "std_price": std_price,
            "final_score": final_score,
            "risk_level": risk_level,
            "feedback": feedback
        }
        log_path = "logs.csv"
        if os.path.exists(log_path):
            existing = pd.read_csv(log_path)
            new_log = pd.DataFrame([log_data])
            pd.concat([existing, new_log]).to_csv(log_path, index=False)
        else:
            pd.DataFrame([log_data]).to_csv(log_path, index=False)
        st.success("Feedback recorded successfully!")
