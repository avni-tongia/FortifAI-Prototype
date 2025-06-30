
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

def get_price_anomaly_score(price, category, brand, stats_df):
    group_key = f"{category}_{brand}"
    group_stats = stats_df[stats_df['group_key'] == group_key]
    if not group_stats.empty:
        mean = group_stats['rolling_mean'].values[0]
        std = group_stats['rolling_std'].values[0]
        if std > 0:
            z_score = abs((price - mean) / std)
        else:
            z_score = 0.0
        scaler = MinMaxScaler()
        score = scaler.fit_transform(np.array([[z_score]])).flatten()[0]
        return score
    return 0.0

try:
    legit_text_pool = pickle.load(open('../legit_text_pool.pkl', 'rb'))
    fraud_text_pool = pickle.load(open('../fraud_text_pool.pkl', 'rb'))
    legit_image_embeddings = np.load('../legit_image_embeddings.npy')
    price_stats_df = pd.read_csv('../price_stats.csv')
except:
    st.error("Required files not found. Please ensure embeddings and stats files are in place.")
    st.stop()

st.set_page_config(page_title="Product Fraud Detection", layout="wide")
st.title("🛡️ Product Listing Fraud Detection System")

uploaded_file = st.file_uploader("Upload Product Image", type=['jpg', 'jpeg', 'png'])
product_text = st.text_area("Enter Product Title/Description")
product_price = st.number_input("Enter Product Price (INR)", min_value=0.0, format="%.2f")
category = st.text_input("Enter Product Category")
brand = st.text_input("Enter Product Brand")

if uploaded_file and product_text and product_price and category and brand:
    image_embedding = get_image_embedding(uploaded_file)
    text_embedding = get_text_embedding(product_text)

    text_legit_sim = cosine_similarity([text_embedding], legit_text_pool).max()
    text_fraud_sim = cosine_similarity([text_embedding], fraud_text_pool).max()
    text_score = max(0, text_fraud_sim - text_legit_sim)

    image_sim = cosine_similarity([image_embedding], legit_image_embeddings).max()
    image_score = 1 - image_sim

    price_anomaly_score = get_price_anomaly_score(product_price, category, brand, price_stats_df)

    final_score = np.clip((0.4 * text_score + 0.4 * price_anomaly_score + 0.2 * image_score), 0, 1)

    if final_score >= 0.75:
        risk_level = "High Risk"
    elif final_score >= 0.4:
        risk_level = "Moderate Risk"
    else:
        risk_level = "Low Risk"

    st.markdown(f"### 🧮 Fraud Risk Score: **{final_score:.2f}** — {risk_level}")

    st.markdown("#### 📊 Contribution Breakdown")
    labels = ['Text', 'Image', 'Price']
    scores = [text_score, image_score, price_anomaly_score]
    fig, ax = plt.subplots()
    ax.barh(labels, scores, color='orange')
    ax.set_xlim(0, 1)
    st.pyplot(fig)

    st.markdown("#### 📝 Moderator Feedback")
    feedback = st.radio("Is this prediction correct?", ["Correct (Fraud)", "Incorrect (Legit)"])
    if st.button("Submit Feedback"):
        log_data = {
            "timestamp": datetime.datetime.now(),
            "description": product_text,
            "price": product_price,
            "category": category,
            "brand": brand,
            "text_score": text_score,
            "image_score": image_score,
            "price_score": price_anomaly_score,
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
