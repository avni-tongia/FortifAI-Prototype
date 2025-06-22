
import pandas as pd
import pickle
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv("transaction_bootstrap_pool.csv")

label_enc_ip = LabelEncoder()
df['ip_country_encoded'] = label_enc_ip.fit_transform(df['ip_country'])

label_enc_vpn = LabelEncoder()
df['vpn_used_encoded'] = label_enc_vpn.fit_transform(df['vpn_used'])

features = [
    'device_id', 'ip_country_encoded', 'time_of_purchase',
    'cart_total', 'account_age_days', 'browser_fingerprint', 'vpn_used_encoded'
]

X = df[features].values
y = df['label'].values

model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X, y)

with open('xgb_transaction_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('label_encoder_ip.pkl', 'wb') as f:
    pickle.dump(label_enc_ip, f)
with open('label_encoder_vpn.pkl', 'wb') as f:
    pickle.dump(label_enc_vpn, f)

print("✅ Transaction model trained and saved.")
