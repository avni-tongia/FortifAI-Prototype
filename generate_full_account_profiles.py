import pandas as pd
import random


# Synthetic Account Profile Generator for Testing
# Generates behavioral data for 20 simulated user accounts


account_profiles = []

for account_id in range(1, 501):
    total_orders = random.randint(0, 100)
    total_spend = total_orders * random.uniform(50, 300)
    avg_order_value = total_spend / total_orders if total_orders > 0 else 0
    first_time_buyer = 1 if total_orders == 0 else 0
    past_chargebacks = random.randint(0, min(total_orders, 5))

    # Simulated behavioral attributes
    avg_session_length = random.uniform(30, 900)  # in seconds
    avg_form_fill_time = random.uniform(2, 15)    # in seconds
    #click_pattern_abnormality = random.uniform(0, 1)  # 0 = normal, 1 = high anomaly

    profile = {
        'account_id': f'ACC{account_id:03d}',
        'total_orders': total_orders,
        'total_spend': round(total_spend, 2),
        'avg_order_value': round(avg_order_value, 2),
        'first_time_buyer': first_time_buyer,
        'past_chargebacks': past_chargebacks,
        'avg_session_length': round(avg_session_length, 2),
        'avg_form_fill_time': round(avg_form_fill_time, 2),
        #'click_pattern_abnormality': round(click_pattern_abnormality, 2)
    }

    account_profiles.append(profile)

# Export to CSV for use in fraud detection models
df_profiles = pd.DataFrame(account_profiles)
df_profiles.to_csv("account_profiles_v2.csv", index=False)

print("Account profile dataset saved as 'account_profiles_v2.csv'.")
