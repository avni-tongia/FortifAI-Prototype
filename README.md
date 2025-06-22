
# End-to-End Fraud Detection Model


# Modules Included

- `app.py` → Streamlit multi-page entry point  
- `pages/1_Product_Listing.py` → Detection of Product Listing Fraud (Image + Text Embedding)  
- `pages/2_Buyer_Transaction.py` → Transaction Fraud with Behavioral Profile Referencing
- `pages/3_Review_Detection` → LLM based AI generated review detection and fraud review ring detection
- `page/4_Return_Fraud_Detection` → Comparing listing and return images to detect fraud
- `initalize_listing_text_image_pools.py` → Initialising Pool generator for image + text  
- `generate_full_account_profiles.py` → Behavioral Account Profile Generator 
- `train_behaviour_model.py` → Self-learning trainer using behavioral data 
- `account_profiles_v2.csv` → Behavioral account profiles database  
- `xgb_transaction_model_v2.pkl` → Trained behavioral model  
- `label_encoder_ip_v2.pkl` → IP encoder 
- `label_encoder_vpn_v2.pkl` → VPN encoder
- `Dockerfile` → Docker deployment file  
- `requirements.txt` → All dependencies  
- `.gitignore` → Clean repo tracking

# Virtual Environment Creation

```bash
python -m venv venv
```

# Activating venv:

- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

## Install Required Libraries

```bash
pip install -r requirements.txt
```

## Initialize Product Listing Pools

```bash
python initialize_listing_text_image_pools.py
```

Generates:

- `legit_text_pool.pkl`  
- `fraud_text_pool.pkl`  
- `legit_image_pool.pkl`  
- `fraud_image_pool.pkl`

---

# Transaction Behavioral Model

# Generate Behavioral Account Profiles

```bash
python generate_full_account_profiles.py
```

Generates:

- `account_profiles_v2.csv` (profile database)

---

# Train Behavioral Model

```bash
python train_behaviour_model.py
```

Generates:

- `xgb_transaction_model_v2.pkl`  
- `label_encoder_ip_v2.pkl`  
- `label_encoder_vpn_v2.pkl`

---

## Run Streamlit App

```bash
streamlit run .
```

Access browser: `http://localhost:8501`