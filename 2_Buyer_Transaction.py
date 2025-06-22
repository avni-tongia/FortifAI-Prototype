
import streamlit as st
import numpy as np
import pickle
import random
import datetime

# -----------------------------------------------------
# 🔷 Load trained XGBoost model and label encoders
# -----------------------------------------------------
model = pickle.load(open('xgb_transaction_model.pkl', 'rb'))
label_enc_ip = pickle.load(open('label_encoder_ip.pkl', 'rb'))
label_enc_vpn = pickle.load(open('label_encoder_vpn.pkl', 'rb'))

# -----------------------------------------------------
# 🔷 Streamlit UI Section for Transaction Fraud Page
# -----------------------------------------------------
st.title("💳 Buyer Transaction Fraud Detection")

st.markdown("🛈 **Note:** Most transaction features (IP, device ID, VPN, fingerprint) are collected automatically for security monitoring.")

# -----------------------------------------------------
# 🔷 Collect only minimal real inputs (Cart Total + Account Age)
# -----------------------------------------------------
cart_total = st.number_input("Cart Total ($)", 0.0, 5000.0, 100.0)
account_age_days = st.number_input("Account Age (days)", 0, 365, 100)

if st.button("Simulate Transaction"):

    # -----------------------------------------------------
    # 🔷 Auto-generate remaining features realistically
    # -----------------------------------------------------
    device_id = random.randint(1000, 9999)
    ip_country = random.choice(['US', 'IN', 'CN', 'RU', 'BR', 'NG', 'DE', 'JP'])
    time_of_purchase = datetime.datetime.now().hour
    browser_fingerprint = random.randint(100000, 999999)
    vpn_used = random.choices(['Yes', 'No'], weights=[0.3, 0.7])[0]

    # Display auto-generated fields for user transparency
    st.write("🔎 Auto-generated features:")
    st.write(f"- Device ID: {device_id}")
    st.write(f"- IP Country: {ip_country}")
    st.write(f"- Time of Purchase: {time_of_purchase}")
    st.write(f"- Browser Fingerprint: {browser_fingerprint}")
    st.write(f"- VPN Used: {vpn_used}")

    # -----------------------------------------------------
    # 🔷 Encode categorical variables for model inference
    # -----------------------------------------------------
    ip_encoded = label_enc_ip.transform([ip_country])[0]
    vpn_encoded = label_enc_vpn.transform([vpn_used])[0]

    features = np.array([[device_id, ip_encoded, time_of_purchase,
                          cart_total, account_age_days, browser_fingerprint, vpn_encoded]])

    # -----------------------------------------------------
    # 🔷 Run model inference and display fraud probability
    # -----------------------------------------------------
    fraud_proba = model.predict_proba(features)[0][1]
    st.subheader(f"Fraud Probability: {fraud_proba*100:.2f}%")

    if fraud_proba > 0.80:
        st.error("❌ Transaction BLOCKED — High Risk")
    else:
        st.success("✅ Transaction Approved")
