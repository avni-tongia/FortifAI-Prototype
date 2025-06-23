import streamlit as st
import numpy as np
import pandas as pd
import pickle
import random
import datetime
import os

st.set_page_config(
    page_title="Buyer Transaction Fraud Detection",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Load pre-trained fraud detection model and encoders
model = pickle.load(open('xgb_transaction_model_v2.pkl', 'rb'))
label_enc_ip = pickle.load(open('label_encoder_ip_v2.pkl', 'rb'))
label_enc_vpn = pickle.load(open('label_encoder_vpn_v2.pkl', 'rb'))

# Load account profile dataset for user-specific behavioral features
profile_path = "account_profiles_v2.csv"
if not os.path.exists(profile_path):
    st.error("The required file 'account_profiles_v2.csv' was not found.")
    st.stop()

account_df = pd.read_csv(profile_path)

# Streamlit UI Setup

st.title("Buyer Transaction Fraud Detection")

# User inputs: basic transaction details
account_id = st.text_input("Enter Account ID (e.g., ACC001):")
cart_total = st.number_input("Cart Total ($)", min_value=0.0, max_value=10000.0, value=100.0)
account_age_days = st.number_input("Account Age (days)", min_value=0, max_value=1000, value=100)


# Main Logic: Check if account exists, then run fraud model
if account_id and account_id in account_df['account_id'].values:
    prof_row = account_df[account_df['account_id'] == account_id].iloc[0]

    # Display behavioral attributes for transparency and debugging
    st.subheader("Account Behavioral Profile")
    st.write(f"Total Orders: {prof_row['total_orders']}")
    st.write(f"Total Spend: ${prof_row['total_spend']}")
    st.write(f"Average Order Value: ${prof_row['avg_order_value']}")
    st.write(f"First Time Buyer: {'Yes' if prof_row['first_time_buyer'] == 1 else 'No'}")
    st.write(f"Past Chargebacks: {prof_row['past_chargebacks']}")
    st.write(f"Avg Session Length: {prof_row['avg_session_length']} sec")
    st.write(f"Avg Form Fill Time: {prof_row['avg_form_fill_time']} sec")
    st.write(f"Click Abnormality Score: {prof_row['click_pattern_abnormality']}")

    # Simulate session-level runtime features (normally tracked in production)
    device_id = random.randint(1000, 9999)
    ip_country = random.choice(['US', 'IN', 'CN', 'RU', 'BR', 'NG', 'DE', 'JP'])
    time_of_purchase = datetime.datetime.now().hour
    browser_fingerprint = random.randint(100000, 999999)
    vpn_used = random.choices(['Yes', 'No'], weights=[0.7, 0.3])[0]

    st.write(f"Device ID: {device_id}, IP Country: {ip_country}, VPN Used: {vpn_used}")

    # Encode categorical fields for model input
    ip_encoded = label_enc_ip.transform([ip_country])[0]
    vpn_encoded = label_enc_vpn.transform([vpn_used])[0]

    # Construct feature vector for prediction
    full_features = np.array([[  # ONLY the 12 features used in training
    prof_row['total_orders'],
    prof_row['total_spend'],
    prof_row['avg_order_value'],
    prof_row['first_time_buyer'],
    prof_row['past_chargebacks'],
    prof_row['avg_session_length'],
    prof_row['avg_form_fill_time'],
    prof_row['click_pattern_abnormality'],
    cart_total,
    account_age_days,
    vpn_encoded,
    ip_encoded
        ]])


    # Predict fraud probability
    fraud_proba = model.predict_proba(full_features)[0][1]

    st.subheader("Fraud Probability")
    st.write(f"{fraud_proba * 100:.2f}%")

    # Decision threshold: block if fraud score exceeds 80%
    if fraud_proba > 0.80:
        st.error("Transaction BLOCKED due to high fraud risk.")
    else:
        st.success("Transaction Approved.")

elif account_id:
    st.warning("Account ID not found in database.")
