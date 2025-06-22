
# 🛡️ Unified Self-Learning Multimodal + Transaction Fraud Detection System

---

## ✅ What's Included

- `app.py` → Streamlit multi-page entry point
- `pages/1_Product_Listing.py` → Product Listing Fraud (Image + Text Embedding)
- `pages/2_Buyer_Transaction.py` → Simplified Transaction Fraud (Reduced Inputs)
- `generate_full_combined_initializer.py` → Pool generator for image + text
- `generate_transaction_bootstrap.py` → Bootstrap synthetic transaction dataset
- `train_transaction_model.py` → Train transaction model (XGBoost)
- `Dockerfile` → Docker deployment file
- `requirements.txt` → All dependencies
- `.gitignore` → Clean repo tracking

---

## 🔧 GitHub Structure Best Practices

When pushing to GitHub, ensure you **DO NOT commit**:

- `venv/` folder
- `.pkl` model or embedding files
- Generated image augmentation folders

Your `.gitignore` should include:

```
venv/
__pycache__/
*.pkl
generated_legit_images/
generated_fraud_images/
```

---

# 🚀 Full Setup Instructions

## 1️⃣ Clone Repository

```bash
git clone <your-repo-url>
cd <repo-folder>
```

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

### Activate venv:

- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

✅ Installs:

- streamlit
- torch
- torchvision
- sentence-transformers
- scikit-learn
- pillow
- numpy
- xgboost
- pandas

---

## 4️⃣ Initialize Product Listing Pools

```bash
python generate_full_combined_initializer.py
```

This generates:

- `legit_text_pool.pkl`
- `fraud_text_pool.pkl`
- `legit_image_pool.pkl`
- `fraud_image_pool.pkl`

---

## 5️⃣ Initialize Transaction Component

```bash
python generate_transaction_bootstrap.py
python train_transaction_model.py
```

This generates:

- `transaction_bootstrap_pool.csv`
- `xgb_transaction_model.pkl`
- `label_encoder_ip.pkl`
- `label_encoder_vpn.pkl`

---

## 6️⃣ Run Streamlit App

```bash
streamlit run app.py
```

Access in browser: `http://localhost:8501`

✅ Now you have two fully functional pages:

- **Page 1:** Product Listing Fraud Detection (semantic embeddings)
- **Page 2:** Buyer Transaction Fraud Detection (production-style reduced-input simulator)

---

## 🔁 Daily Workflow Summary

| Task | Required? |
|------|------------|
| Reinstall dependencies? | ❌ No |
| Re-initialize pools? | ❌ No (unless resetting data) |
| Activate venv? | ✅ Yes |
| Launch Streamlit? | ✅ Yes |

---

# 🔨 Optional Docker Deployment

### Build Docker Image

```bash
docker build -t unified-fraud-detector .
```

### Run Docker Container

```bash
docker run -p 8501:8501 unified-fraud-detector
```

Access browser as usual: `http://localhost:8501`

---

# ✅ After This Setup

- Clean production-grade repo structure.
- Virtual environment fully isolated from Git.
- Full reproducibility using `requirements.txt`.

---

