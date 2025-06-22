import pandas as pd
import numpy as np
import pickle
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
import random

# Standalone Phase 2 Training Script for Transaction Fraud Model

# Load account-level behavioral profiles
profile_df = pd.read_csv("account_profiles_v2.csv")

# Generate synthetic transaction data for each account
synthetic_transactions = []

for index, row in profile_df.iterrows():
    # Each account generates between 10 and 50 transactions
    for _ in range(random.randint(10, 50)):
        device_id = random.randint(1000, 9999)
        ip_country = random.choice(['US', 'IN', 'CN', 'RU', 'BR', 'NG', 'DE', 'JP'])
        time_of_purchase = random.randint(0, 23)
        cart_total = random.uniform(50, 5000)
        account_age_days = random.randint(0, 365)
        browser_fingerprint = random.randint(100000, 999999)
        vpn_used = random.choice(['Yes', 'No'])

        # Rule-based fraud label: early account + high cart + VPN
        fraud_label = 1 if vpn_used == 'Yes' and account_age_days < 30 and cart_total > 2000 else 0

        transaction = {
            'account_id': row['account_id'],
            'device_id': device_id,
            'ip_country': ip_country,
            'time_of_purchase': time_of_purchase,
            'cart_total': cart_total,
            'account_age_days': account_age_days,
            'browser_fingerprint': browser_fingerprint,
            'vpn_used': vpn_used,
            'label': fraud_label,
            'total_orders': row['total_orders'],
            'total_spend': row['total_spend'],
            'avg_order_value': row['avg_order_value'],
            'first_time_buyer': row['first_time_buyer'],
            'past_chargebacks': row['past_chargebacks'],
            'avg_session_length': row['avg_session_length'],
            'avg_form_fill_time': row['avg_form_fill_time'],
            'click_pattern_abnormality': row['click_pattern_abnormality']
        }

        synthetic_transactions.append(transaction)

# Convert the transaction list to a DataFrame
df = pd.DataFrame(synthetic_transactions)

# Encode categorical fields for modeling
label_enc_ip = LabelEncoder()
df['ip_country_encoded'] = label_enc_ip.fit_transform(df['ip_country'])

label_enc_vpn = LabelEncoder()
df['vpn_used_encoded'] = label_enc_vpn.fit_transform(df['vpn_used'])

# Define feature set for model training
features = [
    'device_id', 'ip_country_encoded', 'time_of_purchase',
    'cart_total', 'account_age_days', 'browser_fingerprint', 'vpn_used_encoded',
    'total_orders', 'total_spend', 'avg_order_value',
    'first_time_buyer', 'past_chargebacks',
    'avg_session_length', 'avg_form_fill_time', 'click_pattern_abnormality'
]

X = df[features].values
y = df['label'].values

# Train XGBoost classification model
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X, y)

# Save trained model and encoders
with open('xgb_transaction_model_v2.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('label_encoder_ip_v2.pkl', 'wb') as f:
    pickle.dump(label_enc_ip, f)

with open('label_encoder_vpn_v2.pkl', 'wb') as f:
    pickle.dump(label_enc_vpn, f)

print("Standalone Phase 2 training completed. Model and encoders saved.")
