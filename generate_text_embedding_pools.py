
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import random

# Load pre-trained SentenceTransformer model
text_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Legitimate product titles (you can update this list)
legit_text_samples = [
    "Apple iPhone 15 Pro Max",
    "Sony WH-1000XM5 Headphones",
    "Adidas Ultraboost Running Shoes",
    "Nike Air Jordan 1 Retro High OG",
    "Gucci Ophidia GG Handbag",
    "Omega Seamaster Diver 300M Watch"
]

# Fraud patterns + common scam brand names (feel free to expand)
fraud_patterns = [
    "AAA Grade {brand}",
    "{brand} 1:1 OG Copy",
    "Supercopy {brand} Premium Replica",
    "Luxury Mirror Copy {brand}",
    "Original Quality {brand} Super Replica",
    "{brand} VIP Master Replica Collection"
]
brands = ["Nike Air Jordan", "Gucci Bag", "Chanel Purse", "Rolex Watch", "Omega Seamaster", "Adidas Yeezy"]

# Dynamically create 50 synthetic fraud text examples
fraud_text_samples = [
    random.choice(fraud_patterns).format(brand=random.choice(brands))
    for _ in range(50)
]

# Encode both pools
legit_text_embeddings = np.array([text_model.encode(text) for text in legit_text_samples])
fraud_text_embeddings = np.array([text_model.encode(text) for text in fraud_text_samples])

# Save to disk
with open("legit_text_pool.pkl", "wb") as f:
    pickle.dump(legit_text_embeddings, f)

with open("fraud_text_pool.pkl", "wb") as f:
    pickle.dump(fraud_text_embeddings, f)

print("✅ Legit and fraud text pools regenerated successfully.")
