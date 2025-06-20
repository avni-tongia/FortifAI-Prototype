
# 🛡️ Fully Commented Self-Learning Multimodal Fraud Detection System (Text + Image)

---

## ✅ Components:

- `app.py` → Streamlit App (fully self-learning system)
- `generate_full_combined_initializer.py` → Auto-generator for text & image embedding pools
- `Dockerfile` → Full dockerized deployment

---

## 🚀 Full Instructions:

### 1️⃣ Prepare your initial images

In repo folder place:

- `legit_sample1.jpg`
- `legit_sample2.jpg`
- `fraud_sample1.jpg`
- `fraud_sample2.jpg`

### 2️⃣ Generate embedding pools:

```bash
python generate_full_combined_initializer.py
```

This will generate all `.pkl` embedding pools.

### 3️⃣ Build Docker image:

```bash
docker build -t multimodal-fraud-detector .
```

### 4️⃣ Run Docker container:

```bash
docker run -p 8501:8501 multimodal-fraud-detector
```

### 5️⃣ Open browser: `http://localhost:8501`

✅ Fully working system — ready for self-learning deployment.

---

## 🏗️ Enterprise scalable foundation.

