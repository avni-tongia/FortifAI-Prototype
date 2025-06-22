
import streamlit as st
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle


text_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

resnet = models.resnet152(pretrained=True)
resnet.eval()
resnet = torch.nn.Sequential(*(list(resnet.children())[:-1]))

#ResNet input
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

try:
    legit_text_pool = pickle.load(open('legit_text_pool.pkl', 'rb'))
    fraud_text_pool = pickle.load(open('fraud_text_pool.pkl', 'rb'))
    legit_image_pool = pickle.load(open('legit_image_pool.pkl', 'rb'))
    fraud_image_pool = pickle.load(open('fraud_image_pool.pkl', 'rb'))
except:
    st.error("❌ Embedding pools not found. Please run initializer first.")
    st.stop()

#Streamlit

st.title("🛒 Product Listing Fraud Detection")

uploaded_file = st.file_uploader("Upload Product Image", type=['jpg', 'jpeg', 'png'])
product_text = st.text_area("Enter Product Title/Description")

# Fraud detection
if uploaded_file and product_text:
    image_embedding = get_image_embedding(uploaded_file)
    text_embedding = get_text_embedding(product_text)

    legit_text_sim = cosine_similarity([text_embedding], legit_text_pool).max()
    fraud_text_sim = cosine_similarity([text_embedding], fraud_text_pool).max()
    legit_image_sim = cosine_similarity([image_embedding], legit_image_pool).max()
    fraud_image_sim = cosine_similarity([image_embedding], fraud_image_pool).max()

    st.write(f"📝 Text Legit: {legit_text_sim:.2f} | Fraud: {fraud_text_sim:.2f}")
    st.write(f"🖼️ Image Legit: {legit_image_sim:.2f} | Fraud: {fraud_image_sim:.2f}")

    # Decision thresholding
    if (fraud_text_sim > 0.8 and fraud_text_sim > legit_text_sim) or        (fraud_image_sim > 0.8 and fraud_image_sim > legit_image_sim):
        st.error("❌ Product quarantined due to high fraud risk.")
        feedback = st.radio("Moderator Feedback:", ["Correct (Fraud)", "Incorrect (Legit)"])
        if st.button("Submit Feedback"):
            st.success("✅ Feedback recorded.")
    else:
        st.success("✅ Product cleared successfully.")
