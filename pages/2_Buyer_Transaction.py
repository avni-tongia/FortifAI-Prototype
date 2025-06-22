
import streamlit as st
import numpy as np
import pandas as pd
import pickle
import random
import datetime
import os

# --------------------------------------------------------
# Load full upgraded model and encoders
# --------------------------------------------------------
model = pickle.load(open('xgb_transaction_model_v2.pkl', 'rb'))
label_enc_ip = pickle.load(open('label_encoder_ip_v2.pkl', 'rb'))
label_enc_vpn = pickle.load(open('label_encoder_vpn_v2.pkl', 'rb'))

# Load behavioral profiles
profile_path = "account_profiles_v2.csv"
if not os.path.exists(profile_path):
    st.error("account_profiles_v2.csv not found")
    st.stop()

account_df = pd.read_csv(profile_path)

# --------------------------------------------------------
# Streamlit UI (Phase 2 upgraded)
# --------------------------------------------------------
st.title("💳 Buyer Transaction Fraud Detection (Behavioral Integrated)")
account_id = st.text_input("Enter Account ID (e.g., ACC001):")
cart_total = st.number_input("Cart Total ($)", 0.0, 10000.0, 100.0)
account_age_days = st.number_input("Account Age (days)", 0, 1000, 100)

if account_id and account_id in account_df['account_id'].values:
    prof_row = account_df[account_df['account_id'] == account_id].iloc[0]

    # Display Behavioral Profile
    st.subheader("📊 Account Behavioral Profile")
    st.write(f"- Total Orders: {prof_row['total_orders']}")
    st.write(f"- Total Spend: ${prof_row['total_spend']}")
    st.write(f"- Average Order Value: ${prof_row['avg_order_value']}")
    st.write(f"- First Time Buyer: {'Yes' if prof_row['first_time_buyer']==1 else 'No'}")
    st.write(f"- Past Chargebacks: {prof_row['past_chargebacks']}")
    st.write(f"- Avg Session Length: {prof_row['avg_session_length']} sec")
    st.write(f"- Avg Form Fill Time: {prof_row['avg_form_fill_time']} sec")
    st.write(f"- Click Abnormality Score: {prof_row['click_pattern_abnormality']}")

    # Auto-generated session-level features
    device_id = random.randint(1000, 9999)
    ip_country = random.choice(['US', 'IN', 'CN', 'RU', 'BR', 'NG', 'DE', 'JP'])
    time_of_purchase = datetime.datetime.now().hour
    browser_fingerprint = random.randint(100000, 999999)
    #    vpn_used = random.choices(['Yes', 'No'], weights=[0.3, 0.7])[0]
    vpn_used = 'Yes'

    st.write(f"Device ID: {device_id}, IP Country: {ip_country}, VPN: {vpn_used}")

    ip_encoded = label_enc_ip.transform([ip_country])[0]
    vpn_encoded = label_enc_vpn.transform([vpn_used])[0]

    full_features = np.array([
        [device_id, ip_encoded, time_of_purchase, cart_total, account_age_days,
         browser_fingerprint, vpn_encoded,
         prof_row['total_orders'], prof_row['total_spend'], prof_row['avg_order_value'],
         prof_row['first_time_buyer'], prof_row['past_chargebacks'],
         prof_row['avg_session_length'], prof_row['avg_form_fill_time'],
         prof_row['click_pattern_abnormality']]
    ])

    fraud_proba = model.predict_proba(full_features)[0][1]
    st.subheader(f"Fraud Probability: {fraud_proba*100:.2f}%")

    if fraud_proba > 0.80:
        st.error("❌ Transaction BLOCKED")
    else:
        st.success("✅ Transaction Approved")
elif account_id:
    st.warning("Account ID not found.")
