
import streamlit as st
import numpy as np
import pandas as pd
import pickle
import random
import datetime
import os
import shap

st.set_page_config(
    page_title="Buyer Transaction Fraud Detection",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("<div style='margin-top: -60px'></div>", unsafe_allow_html=True)
st.markdown(
    "<h1 style='text-align: center; color: #ff9900;'>🛡️ Buyer Transaction Fraud Detection</h1>", 
    unsafe_allow_html=True
)

# Load model and encoders
model = pickle.load(open('xgb_transaction_model_v2.pkl', 'rb'))
label_enc_ip = pickle.load(open('label_encoder_ip_v2.pkl', 'rb'))
label_enc_vpn = pickle.load(open('label_encoder_vpn_v2.pkl', 'rb'))
explainer = shap.TreeExplainer(model)

# Load account data
profile_path = "account_profiles_v2.csv"
if not os.path.exists(profile_path):
    st.error("The required file 'account_profiles_v2.csv' was not found.")
    st.stop()
account_df = pd.read_csv(profile_path)

# Input Section
st.markdown("### 🔍 Input Transaction Details")
col1, col2 = st.columns(2)
with col1:
    account_id = st.text_input("🆔 Enter Account ID (e.g., ACC001):")
    cart_total = st.number_input("🛒 Cart Total ($)", min_value=0.0, max_value=10000.0, value=100.0)
with col2:
    account_age_days = st.number_input("📅 Account Age (days)", min_value=0, max_value=1000, value=100)
    ip_country = st.selectbox("🌍 Select IP Country", ['US', 'IN', 'RU', 'CN', 'NG', 'BR', 'DE', 'FR', 'AU', 'SG'])

# VPN used input
_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    left, right = st.columns([1, 2])  # inner layout
    with right:
        st.markdown("🔐 Was VPN used?", unsafe_allow_html=True)
        vpn_used = st.radio("VPN Used", options=['Yes', 'No'], horizontal=True, label_visibility="collapsed")

# Processing logic
if account_id and account_id in account_df['account_id'].values:
    prof_row = account_df[account_df['account_id'] == account_id].iloc[0]

    # Encode categorical fields
    ip_encoded = label_enc_ip.transform([ip_country])[0]
    vpn_encoded = label_enc_vpn.transform([vpn_used])[0]

    full_features = np.array([[
        prof_row['total_orders'],
        prof_row['total_spend'],
        prof_row['avg_order_value'],
        prof_row['first_time_buyer'],
        prof_row['past_chargebacks'],
        prof_row['avg_session_length'],
        prof_row['avg_form_fill_time'],
        cart_total,
        account_age_days,
        vpn_encoded,
        ip_encoded
    ]])

    # Predict and interpret
    fraud_proba = model.predict_proba(full_features)[0][1]
    risk_bucket = "No Risk" if fraud_proba <= 0.4 else "Moderate Risk" if fraud_proba <= 0.8 else "High Risk"

    shap_values = explainer.shap_values(full_features)
    shap_vals = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]
    feature_names = [
        'total_orders', 'total_spend', 'avg_order_value', 'first_time_buyer',
        'past_chargebacks', 'avg_session_length', 'avg_form_fill_time',
        'cart_total', 'account_age_days', 'vpn_encoded', 'ip_encoded'
    ]
    most_important_index = np.argmax(np.abs(shap_vals))
    most_important_feature = feature_names[most_important_index]

    # Determine card color
    card_color = "#e6f7e6" if risk_bucket == "No Risk" else "#fff5cc" if risk_bucket == "Moderate Risk" else "#ffe6e6"
    border_color = "#28a745" if risk_bucket == "No Risk" else "#ffc107" if risk_bucket == "Moderate Risk" else "#dc3545"

    # Layout: card view below input fields
    col1, col2 = st.columns([1.8, 1.2])

    with col1:
        st.markdown("""
            <div style='display: flex; border: 1px solid #ddd; border-radius: 10px; background-color: #ffffff; color: #000000; box-shadow: 2px 2px 6px rgba(0,0,0,0.05);'>
                <div style='width: 25%; display: flex; align-items: center; justify-content: center; font-size: 120px; background-color: #f0f0f0; border-top-left-radius: 10px; border-bottom-left-radius: 10px;'>
                    👤
                </div>
                <div style='width: 75%; padding: 20px;'>
                    <h4 style='margin-bottom: 20px; color: #232f3e;'>Account Behavioral Profile</h4>
                    <div style='display: flex; gap: 40px;'>
                        <div>
                            <p>Total Orders: <strong>{0}</strong></p>
                            <p>Total Spend: <strong>${1}</strong></p>
                            <p>Average Order Value: <strong>${2}</strong></p>
                            <p>Past Chargebacks: <strong>{3}</strong></p>
                        </div>
                        <div>
                            <p>First Time Buyer: <strong>{4}</strong></p>
                            <p>Avg Session Length: <strong>{5}s</strong></p>
                            <p>Avg Form Fill Time: <strong>{6}s</strong></p>
                        </div>
                    </div>
                </div>
            </div>
        """.format(
            prof_row['total_orders'],
            prof_row['total_spend'],
            prof_row['avg_order_value'],
            prof_row['past_chargebacks'],
            'Yes' if prof_row['first_time_buyer'] == 1 else 'No',
            prof_row['avg_session_length'],
            prof_row['avg_form_fill_time']
        ), unsafe_allow_html=True)


    with col2:
        st.markdown(f"""
            <div style='min-height: 245px; border: 2px solid {border_color}; border-radius: 10px; padding: 20px; background-color: {card_color}; color: #000000; box-shadow: 2px 2px 6px rgba(0,0,0,0.08);'>
                <h4 style='margin-bottom: 20px; color: #232f3e;'> Fraud Risk Assessment</h4>
                <p>Fraud Probability: <strong>{fraud_proba * 100:.2f}%</strong></p>
                <p>Key Feature: <strong>{most_important_feature}</strong></p>
                <p>Risk Bucket: <strong>{risk_bucket}</strong></p>
            </div>
        """, unsafe_allow_html=True)

    # Logging
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "account_id": account_id,
        "cart_total": cart_total,
        "account_age_days": account_age_days,
        "ip_country": ip_country,
        "vpn_used": vpn_used,
        "fraud_probability": fraud_proba,
        "risk_bucket": risk_bucket,
        "key_feature": most_important_feature
    }
    log_df = pd.DataFrame([log_entry])
    if os.path.exists("fraud_predictions_log.csv"):
        log_df.to_csv("fraud_predictions_log.csv", mode='a', header=False, index=False)
    else:
        log_df.to_csv("fraud_predictions_log.csv", index=False)

elif account_id:
    st.warning("Account ID not found in database.")
