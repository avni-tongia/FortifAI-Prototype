
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import pickle

# Load generated profiles
profiles = pd.read_csv("account_profiles_v2.csv")

# Create synthetic transactions for each profile
transactions = []
for _, row in profiles.iterrows():
    for _ in range(10):  # simulate multiple transactions per user
        cart_total = np.random.randint(100, 5000)
        account_age_days = np.random.randint(1, 365)
        vpn_used = np.random.choice(['Yes', 'No'])
        ip_country = np.random.choice(['US', 'IN', 'RU', 'CN', 'NG', 'BR', 'DE', 'FR', 'AU', 'SG'])

        # New weighted rule-based fraud label
        fraud_score = 0

        # Past behavioral factors
        if row['past_chargebacks'] > 1:
            fraud_score += 4  # VERY HIGH weight
        if row['first_time_buyer'] == 1:
            fraud_score += 1  

        # Session behavior factors
        #if row['click_pattern_abnormality'] == 1:
            #fraud_score += 2
        if row['avg_form_fill_time'] < 2 or row['avg_form_fill_time'] > 20:
            fraud_score += 2
        if row['avg_session_length'] < 30:
            fraud_score += 1

        # Transaction real-time features
        if vpn_used == 'Yes':
            fraud_score += 2
        if ip_country in ['RU', 'NG', 'CN']:
            fraud_score += 2
        if cart_total > 5000:
            fraud_score += 2
        if account_age_days < 30:
            fraud_score += 1

        # Final label based on threshold score
        fraud_label = 1 if fraud_score >= 5 else 0

        transactions.append({
            'total_orders': row['total_orders'],
            'total_spend': row['total_spend'],
            'avg_order_value': row['avg_order_value'],
            'first_time_buyer': row['first_time_buyer'],
            'past_chargebacks': row['past_chargebacks'],
            'avg_session_length': row['avg_session_length'],
            'avg_form_fill_time': row['avg_form_fill_time'],
            #'click_pattern_abnormality': row['click_pattern_abnormality'],
            'cart_total': cart_total,
            'account_age_days': account_age_days,
            'vpn_used': vpn_used,
            'ip_country': ip_country,
            'fraud_label': fraud_label
        })

# Convert to dataframe
tx = pd.DataFrame(transactions)

# Encode categorical variables
vpn_encoder = LabelEncoder()
ip_encoder = LabelEncoder()

tx['vpn_encoded'] = vpn_encoder.fit_transform(tx['vpn_used'])
tx['ip_encoded'] = ip_encoder.fit_transform(tx['ip_country'])

# Save encoders
with open("label_encoder_vpn_v2.pkl", "wb") as f:
    pickle.dump(vpn_encoder, f)
with open("label_encoder_ip_v2.pkl", "wb") as f:
    pickle.dump(ip_encoder, f)

# Train model
features = ['total_orders', 'total_spend', 'avg_order_value', 'first_time_buyer',
            'past_chargebacks', 'avg_session_length', 'avg_form_fill_time', 'cart_total', 'account_age_days',
            'vpn_encoded', 'ip_encoded']
X = tx[features]
y = tx['fraud_label']

model = XGBClassifier()
model.fit(X, y)

# Save model
with open("xgb_transaction_model_v2.pkl", "wb") as f:
    pickle.dump(model, f)

print("Training complete. Model saved.")
