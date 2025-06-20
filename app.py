
import streamlit as st
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# -------------------------------------------------------
# Load models for text and image embedding generation
# -------------------------------------------------------

# Load Sentence Transformer model for text embeddings (768-dimensional)
text_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Load ResNet-152 pretrained model for image embeddings (2048-dimensional)
resnet = models.resnet152(pretrained=True)
resnet.eval()
# Remove classification head to use only feature extractor layers
resnet = torch.nn.Sequential(*(list(resnet.children())[:-1]))

# -------------------------------------------------------
# Define preprocessing pipeline for incoming product images
# -------------------------------------------------------

transform_pipeline = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize images to match ResNet input size
    transforms.ToTensor(),          # Convert image to tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])  # Normalize to pretrained weights
])

# -------------------------------------------------------
# Define helper functions for embedding generation
# -------------------------------------------------------

# Extract image embedding from uploaded product image
def get_image_embedding(image_bytes):
    image = Image.open(image_bytes).convert('RGB')
    tensor = transform_pipeline(image).unsqueeze(0)
    with torch.no_grad():
        embedding = resnet(tensor).squeeze().numpy()
    return embedding.flatten()

# Extract text embedding from product title/description
def get_text_embedding(text):
    return text_model.encode([text])[0]

# -------------------------------------------------------
# Streamlit Web App UI Section
# -------------------------------------------------------

st.title("🛡️ Self-Learning Multimodal Fraud Detector (Text + Image)")

st.sidebar.title("System Explanation")
st.sidebar.markdown("""
- Uses semantic embeddings for both text & image
- Live fraud detection + real-time self-learning from human feedback
- Fully unsupervised after initial bootstrap initialization
""")

# -------------------------------------------------------
# Load existing initialized embedding pools from disk
# These pools grow automatically as moderators provide feedback.
# -------------------------------------------------------

try:
    legit_text_pool = pickle.load(open('legit_text_pool.pkl', 'rb'))
    fraud_text_pool = pickle.load(open('fraud_text_pool.pkl', 'rb'))
    legit_image_pool = pickle.load(open('legit_image_pool.pkl', 'rb'))
    fraud_image_pool = pickle.load(open('fraud_image_pool.pkl', 'rb'))
except:
    st.error("❌ Embedding pools not found. Please run the initializer first to generate pools.")
    st.stop()

# -------------------------------------------------------
# Get input from user — image upload and product text
# -------------------------------------------------------

uploaded_file = st.file_uploader("Upload Product Image (JPEG/PNG)", type=['jpg', 'jpeg', 'png'])
product_text = st.text_area("Enter Product Title/Description")

# -------------------------------------------------------
# Core detection pipeline: generate embeddings, compute similarity
# -------------------------------------------------------

if uploaded_file and product_text:
    # Generate embeddings for current submission
    image_embedding = get_image_embedding(uploaded_file)
    text_embedding = get_text_embedding(product_text)

    # Compute cosine similarity scores to legit and fraud pools
    legit_text_sim = cosine_similarity([text_embedding], legit_text_pool).max()
    fraud_text_sim = cosine_similarity([text_embedding], fraud_text_pool).max()
    legit_image_sim = cosine_similarity([image_embedding], legit_image_pool).max()
    fraud_image_sim = cosine_similarity([image_embedding], fraud_image_pool).max()

    # Show similarity scores transparently to the moderator
    st.subheader("Similarity Scores")
    st.write(f"📝 Text → Legit Similarity: **{legit_text_sim:.2f}**")
    st.write(f"📝 Text → Fraud Similarity: **{fraud_text_sim:.2f}**")
    st.write(f"🖼️ Image → Legit Similarity: **{legit_image_sim:.2f}**")
    st.write(f"🖼️ Image → Fraud Similarity: **{fraud_image_sim:.2f}**")

    # -------------------------------------------------------
    # Decision Logic: quarantine if either fraud score dominates legit score
    # -------------------------------------------------------

    if (fraud_text_sim > 0.8 and fraud_text_sim > legit_text_sim) or        (fraud_image_sim > 0.8 and fraud_image_sim > legit_image_sim):
        st.error("❌ Product quarantined due to high semantic fraud risk.")

        # Allow moderator to provide feedback for self-learning update
        feedback = st.radio("Moderator Feedback:", ["Correct (Fraud)", "Incorrect (Legit)"])
        if st.button("Submit Feedback"):
            if feedback == "Correct (Fraud)":
                # Add embeddings to fraud pools if moderator confirms fraud
                fraud_text_pool = np.vstack([fraud_text_pool, text_embedding])
                fraud_image_pool = np.vstack([fraud_image_pool, image_embedding])
                pickle.dump(fraud_text_pool, open('fraud_text_pool.pkl', 'wb'))
                pickle.dump(fraud_image_pool, open('fraud_image_pool.pkl', 'wb'))
                st.success("Fraud pools updated.")
            else:
                # Add embeddings to legit pools if moderator confirms legit
                legit_text_pool = np.vstack([legit_text_pool, text_embedding])
                legit_image_pool = np.vstack([legit_image_pool, image_embedding])
                pickle.dump(legit_text_pool, open('legit_text_pool.pkl', 'wb'))
                pickle.dump(legit_image_pool, open('legit_image_pool.pkl', 'wb'))
                st.success("Legit pools updated.")
    else:
        st.success("✅ Product passed fraud detection successfully.")
