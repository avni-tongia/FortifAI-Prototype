
# 🛡️ Unified Self-Learning Multimodal + Behavioral Transaction Fraud Detection System (Phase 2)

---

## ✅ What's Included

- `app.py` → Streamlit multi-page entry point  
- `pages/1_Product_Listing.py` → Product Listing Fraud (Image + Text Embedding)  
- `pages/2_Buyer_Transaction.py` → Fully upgraded Transaction Fraud with Behavioral Profiles  
- `generate_full_combined_initializer.py` → Pool generator for image + text  
- `generate_full_account_profiles.py` → Behavioral Account Profile Generator (Phase 2)  
- `phase2_self_learning_retrainer_standalone.py` → Self-learning standalone retrainer using behavioral data (Phase 2)  
- `account_profiles_v2.csv` → Behavioral account profiles database (generated in Phase 2)  
- `xgb_transaction_model_v2.pkl` → Fully retrained behavioral model (Phase 2)  
- `label_encoder_ip_v2.pkl` → IP encoder (Phase 2)  
- `label_encoder_vpn_v2.pkl` → VPN encoder (Phase 2)  
- `Dockerfile` → Docker deployment file  
- `requirements.txt` → All dependencies  
- `.gitignore` → Clean repo tracking

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
python initalize_listing_text_image_pools.py
```

Generates:

- `legit_text_pool.pkl`  
- `fraud_text_pool.pkl`  
- `legit_image_pool.pkl`  
- `fraud_image_pool.pkl`

---

## 5️⃣ Phase 2 Transaction Behavioral Model

### Generate Behavioral Account Profiles

```bash
python generate_full_account_profiles.py
```

Generates:

- `account_profiles_v2.csv` (profile database)

---

### Train Phase 2 Behavioral Model

```bash
python train_behaviour_model.py
```

Generates:

- `xgb_transaction_model_v2.pkl`  
- `label_encoder_ip_v2.pkl`  
- `label_encoder_vpn_v2.pkl`

---

## 6️⃣ Run Streamlit App

```bash
streamlit run app.py
```

Access browser: `http://localhost:8501`

✅ Now you have two fully functional pages:

- **Page 1:** Product Listing Fraud Detection (Image + Text)  
- **Page 2:** Buyer Transaction Fraud Detection (Behavioral Profile Enhanced — Phase 2)

---

## 🔁 Daily Workflow Summary

| Task | Required? |
|------|------------|
| Reinstall dependencies? | ❌ No |
| Re-run profile generator? | ❌ No (only if adding new accounts) |
| Re-run retrainer? | ✅ Yes (only when updating profiles for self-learning) |
| Activate venv? | ✅ Yes |
| Launch Streamlit? | ✅ Yes |

---

# 🔨 Docker Deployment (Optional)

### Build Docker Image

```bash
docker build -t unified-fraud-detector .
```

### Run Docker Container

```bash
docker run -p 8501:8501 unified-fraud-detector
```

Access browser: `http://localhost:8501`

---

# ✅ After This Setup

- Fully upgraded Phase 2 behavioral model  
- Self-learning retraining infrastructure  
- Clean reproducible multi-modal fraud system  
- Streamlit multi-page deployment

---
