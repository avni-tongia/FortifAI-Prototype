
import pandas as pd
import random

def generate_transaction_row(is_fraud=False):
    device_id = random.randint(1000, 9999)
    ip_country = random.choice(['US', 'IN', 'CN', 'RU', 'BR', 'NG', 'DE', 'JP'])
    time_of_purchase = random.randint(0, 23)
    cart_total = random.uniform(50, 5000)
    account_age_days = random.randint(0, 365 if not is_fraud else 30)
    browser_fingerprint = random.randint(100000, 999999)
    vpn_used = random.choice(['Yes', 'No']) if not is_fraud else 'Yes'
    return {
        'device_id': device_id,
        'ip_country': ip_country,
        'time_of_purchase': time_of_purchase,
        'cart_total': cart_total,
        'account_age_days': account_age_days,
        'browser_fingerprint': browser_fingerprint,
        'vpn_used': vpn_used,
        'label': 1 if is_fraud else 0
    }

legit_data = [generate_transaction_row(is_fraud=False) for _ in range(200)]
fraud_data = [generate_transaction_row(is_fraud=True) for _ in range(200)]
data = legit_data + fraud_data

df = pd.DataFrame(data)
df = df.sample(frac=1).reset_index(drop=True)
df.to_csv("transaction_bootstrap_pool.csv", index=False)

print("✅ Transaction bootstrap dataset generated.")
