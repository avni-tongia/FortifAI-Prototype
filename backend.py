# File: backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import torch
from transformers import pipeline, CLIPProcessor, CLIPModel
from PIL import Image
import torchvision.transforms as transforms
import torchvision.models as models
import os
import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from rapidfuzz import fuzz

app = Flask(__name__)
CORS(app)

# ---------------------------- SETUP ----------------------------

# Load LLM pipeline
text_anomaly_detector = pipeline("text-classification", model="bert-base-uncased")

# Load keywords (suspicious patterns)
with open("brand_typos.json", "r") as f:
    risky_keywords = json.load(f)["keywords"]

# Load master trademark brand list
with open("trademark_brands.json", "r") as f:
    brand_list = json.load(f)["brands"]
FUZZY_THRESHOLD = 85

# Load cached CLIP logo embeddings
with open("logo_embeddings.json", "r") as f:
    brand_logos = {k: np.array(v) for k, v in json.load(f).items()}

# Load CLIP model
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Load pretrained ResNet for image quality check
resnet = models.resnet50(pretrained=True)
resnet.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# ------------------------ TEXT ANALYSIS ------------------------

def detect_text_anomalies(description):
    # Regex flag
    regex_flag = any(re.search(rf"\b{kw}\b", description.lower()) for kw in risky_keywords)

    # Fuzzy matching flag
    fuzzy_matches = []
    words = re.findall(r"\w+", description.lower())
    for word in words:
        for brand in brand_list:
            score = fuzz.ratio(word.lower(), brand.lower())
            if score >= FUZZY_THRESHOLD and word.lower() != brand.lower():
                fuzzy_matches.append((word, brand, score))
    fuzzy_flag = len(fuzzy_matches) > 0

    # LLM-based scoring flag
    prediction = text_anomaly_detector(description[:512])[0]
    llm_flag = prediction['label'] == 'LABEL_1' and prediction['score'] > 0.8

    return regex_flag or fuzzy_flag or llm_flag

# ------------------------ IMAGE ANALYSIS ------------------------

def detect_image_anomalies(image_path):
    image = Image.open(image_path).convert('RGB')
    img_tensor = transform(image).unsqueeze(0)

    # Low confidence ResNet prediction
    with torch.no_grad():
        outputs = resnet(img_tensor)
    confidence = torch.max(torch.nn.functional.softmax(outputs, dim=1)).item()
    low_confidence_flag = confidence < 0.5

    # Logo mismatch via CLIP
    clip_inputs = clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        test_embedding = clip_model.get_image_features(**clip_inputs).squeeze().numpy().reshape(1, -1)

    similarities = [cosine_similarity(test_embedding, ref.reshape(1, -1))[0][0] for ref in brand_logos.values()]
    max_similarity = max(similarities) if similarities else 0
    logo_mismatch_flag = max_similarity < 0.8

    return low_confidence_flag or logo_mismatch_flag

# ------------------------- API ROUTE -------------------------

@app.route('/analyze_listing', methods=['POST'])
def analyze_listing():
    description = request.form.get("description")
    image = request.files.get("image")

    if not description or not image:
        return jsonify({"error": "Missing description or image"}), 400

    img_path = "temp_upload.jpg"
    image.save(img_path)

    text_flag = detect_text_anomalies(description)
    img_flag = detect_image_anomalies(img_path)

    risk_score = 0.9 if text_flag and img_flag else 0.75 if text_flag or img_flag else 0.1

    os.remove(img_path)

    return jsonify({
        "text_flag": text_flag,
        "image_flag": img_flag,
        "risk_score": round(risk_score, 2),
        "action": "quarantine" if risk_score > 0.75 else "approve"
    })

if __name__ == '__main__':
    app.run(debug=True)
