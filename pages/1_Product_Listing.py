
import streamlit as st
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Load pretrained sentence transformer model for text embedding
text_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Load pretrained ResNet-152 model for image embedding
# The final classification layer is removed to extract feature vectors
resnet = models.resnet152(pretrained=True)
resnet.eval()
resnet = torch.nn.Sequential(*(list(resnet.children())[:-1]))

# Define preprocessing pipeline for image input to ResNet
transform_pipeline = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def get_image_embedding(image_bytes):
    """
    Processes an input image and returns its ResNet feature vector.
    """
    image = Image.open(image_bytes).convert('RGB')
    tensor = transform_pipeline(image).unsqueeze(0)
    with torch.no_grad():
        embedding = resnet(tensor).squeeze().numpy()
    return embedding.flatten()

def get_text_embedding(text):
    """
    Converts input product description or title into a sentence embedding.
    """
    return text_model.encode([text])[0]

# Load precomputed embedding pools for legitimate and fraudulent examples
try:
    legit_text_pool = pickle.load(open('legit_text_pool.pkl', 'rb'))
    fraud_text_pool = pickle.load(open('fraud_text_pool.pkl', 'rb'))
    legit_image_pool = pickle.load(open('legit_image_pool.pkl', 'rb'))
    fraud_image_pool = pickle.load(open('fraud_image_pool.pkl', 'rb'))
except:
    st.error("Embedding pools not found. Please run initializer first.")
    st.stop()

# Streamlit interface setup
st.title("Product Listing Fraud Detection")

# File uploader for product image
uploaded_file = st.file_uploader("Upload Product Image", type=['jpg', 'jpeg', 'png'])

# Text input for product title or description
product_text = st.text_area("Enter Product Title/Description")

# If both image and text are provided, run fraud detection
if uploaded_file and product_text:
    # Compute embeddings for the uploaded product image and text
    image_embedding = get_image_embedding(uploaded_file)
    text_embedding = get_text_embedding(product_text)

    # Calculate similarity with known pools
    legit_text_sim = cosine_similarity([text_embedding], legit_text_pool).max()
    fraud_text_sim = cosine_similarity([text_embedding], fraud_text_pool).max()
    legit_image_sim = cosine_similarity([image_embedding], legit_image_pool).max()
    fraud_image_sim = cosine_similarity([image_embedding], fraud_image_pool).max()

    # Display similarity scores
    st.write(f"Text similarity — Legitimate: {legit_text_sim:.2f}, Fraudulent: {fraud_text_sim:.2f}")
    st.write(f"Image similarity — Legitimate: {legit_image_sim:.2f}, Fraudulent: {fraud_image_sim:.2f}")

    # Determine whether to quarantine the product based on similarity thresholds
    if (fraud_text_sim > 0.8 and fraud_text_sim > legit_text_sim) or \
       (fraud_image_sim > 0.8 and fraud_image_sim > legit_image_sim):
        st.error("Product flagged for quarantine due to high fraud risk.")

        # Allow moderator to confirm or reject the system’s classification
        feedback = st.radio("Moderator Feedback:", ["Correct (Fraud)", "Incorrect (Legit)"])
        if st.button("Submit Feedback"):
            st.success("Feedback recorded.")
    else:
        st.success("Product approved for listing.")
