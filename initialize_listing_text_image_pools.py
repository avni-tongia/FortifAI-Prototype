
import pickle
import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image, ImageFilter, ImageEnhance
from sentence_transformers import SentenceTransformer
import random
import os

# -------------------------------------------------------
# Model Loading: Text and Image Embedding Models
# -------------------------------------------------------

# Load pre-trained SentenceTransformer model (768-dim text embeddings)
text_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Load pre-trained ResNet-152 model (2048-dim image embeddings)
resnet = models.resnet152(pretrained=True)
resnet.eval()
resnet = torch.nn.Sequential(*(list(resnet.children())[:-1]))

# -------------------------------------------------------
# Image Preprocessing Pipeline for ResNet model
# -------------------------------------------------------

transform_pipeline = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# -------------------------------------------------------
# Image Embedding Extraction Function
# -------------------------------------------------------

def get_image_embedding(image_path):
    image = Image.open(image_path).convert('RGB')
    tensor = transform_pipeline(image).unsqueeze(0)
    with torch.no_grad():
        embedding = resnet(tensor).squeeze().numpy()
    return embedding.flatten()

# -------------------------------------------------------
# Synthetic Image Augmentation Function for Bootstrapping
# -------------------------------------------------------

def generate_augmented_images(input_path, output_folder, count=5):
    image = Image.open(input_path).convert('RGB')
    for i in range(count):
        augmented = image.copy()
        if random.random() > 0.5:
            augmented = augmented.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))
        if random.random() > 0.5:
            enhancer = ImageEnhance.Contrast(augmented)
            augmented = enhancer.enhance(random.uniform(0.7, 1.3))
        if random.random() > 0.5:
            augmented = augmented.rotate(random.choice([-5, 5, -10, 10]))
        augmented = augmented.resize((300, 300))
        augmented.save(f"{output_folder}/augmented_{i}_{os.path.basename(input_path)}")

# -------------------------------------------------------
# TEXT POOL GENERATION: Legitimate & Synthetic Fraud Examples
# -------------------------------------------------------

# Simulated legitimate product samples (real-world brands)
legit_text_samples = [
    "Apple iPhone 15 Pro Max",
    "Sony WH-1000XM5 Headphones",
    "Adidas Ultraboost Running Shoes",
    "Nike Air Jordan 1 Retro High OG",
    "Gucci Ophidia GG Handbag",
    "Omega Seamaster Diver 300M Watch"
]

# Fraudulent text patterns (typical fraudster marketing language)
fraud_patterns = [
    "AAA Grade {brand}",
    "{brand} 1:1 OG Copy",
    "Supercopy {brand} Premium Replica",
    "Luxury Mirror Copy {brand}",
    "Original Quality {brand} Super Replica",
    "{brand} VIP Master Replica Collection"
]

brands = ["Nike Air Jordan", "Gucci Bag", "Chanel Purse", "Rolex Watch", "Omega Seamaster", "Adidas Yeezy"]

# Generate 50 synthetic fraud text examples dynamically
fraud_text_samples = []
for _ in range(50):
    fraud_text_samples.append(random.choice(fraud_patterns).format(brand=random.choice(brands)))

# Create text embeddings
legit_text_embeddings = np.array([text_model.encode(sample) for sample in legit_text_samples])
fraud_text_embeddings = np.array([text_model.encode(sample) for sample in fraud_text_samples])

# Save text embedding pools to disk
pickle.dump(legit_text_embeddings, open('legit_text_pool.pkl', 'wb'))
pickle.dump(fraud_text_embeddings, open('fraud_text_pool.pkl', 'wb'))

# -------------------------------------------------------
# IMAGE POOL GENERATION: Augmented Images for Legit & Fraud Pools
# -------------------------------------------------------

# You provide 2 legit & 2 fraud seed images manually beforehand:
legit_bases = ['legit_sample1.jpg', 'legit_sample2.jpg']
fraud_bases = ['fraud_sample1.jpg', 'fraud_sample2.jpg']

# Create folders for augmented images
os.makedirs('generated_legit_images', exist_ok=True)
os.makedirs('generated_fraud_images', exist_ok=True)

# Augment fraud image samples
for base in fraud_bases:
    generate_augmented_images(base, 'generated_fraud_images', count=10)

# Augment legit image samples
for base in legit_bases:
    generate_augmented_images(base, 'generated_legit_images', count=10)

# Generate image embeddings from augmented data
legit_image_paths = [os.path.join('generated_legit_images', img) for img in os.listdir('generated_legit_images')]
fraud_image_paths = [os.path.join('generated_fraud_images', img) for img in os.listdir('generated_fraud_images')]

legit_image_embeddings = np.array([get_image_embedding(img) for img in legit_image_paths])
fraud_image_embeddings = np.array([get_image_embedding(img) for img in fraud_image_paths])

# Save image embedding pools to disk
pickle.dump(legit_image_embeddings, open('legit_image_pool.pkl', 'wb'))
pickle.dump(fraud_image_embeddings, open('fraud_image_pool.pkl', 'wb'))

print("✅ Full text + image embedding pools generated successfully!")
