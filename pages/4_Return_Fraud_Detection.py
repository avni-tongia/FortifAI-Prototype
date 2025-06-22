
import streamlit as st
import numpy as np
import pandas as pd
import cv2
import matplotlib.pyplot as plt
from prophet import Prophet

# --------------------------------------------------------
# Image Similarity Check (MSE based)
# --------------------------------------------------------
def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err

def compare_images(img1_path, img2_path, threshold=1500):
    imageA = cv2.imread(img1_path)
    imageB = cv2.imread(img2_path)
    imageA = cv2.resize(imageA, (224, 224))
    imageB = cv2.resize(imageB, (224, 224))
    score = mse(imageA, imageB)
    return score, score > threshold

# --------------------------------------------------------
# Streamlit UI - Return Fraud Detection (Page 4)
# --------------------------------------------------------
st.title("📦 Return Fraud Detection")

st.subheader("Step 1: Image Similarity Check")

col1, col2 = st.columns(2)
with col1:
    original_img = st.file_uploader("Upload Original Product Image", type=['png','jpg','jpeg'])
with col2:
    returned_img = st.file_uploader("Upload Returned Product Image", type=['png','jpg','jpeg'])

if original_img and returned_img:
    with open("original_temp.jpg", "wb") as f:
        f.write(original_img.getbuffer())
    with open("returned_temp.jpg", "wb") as f:
        f.write(returned_img.getbuffer())

    score, mismatch = compare_images("original_temp.jpg", "returned_temp.jpg")
    st.write(f"MSE Score: {score:.2f}")
    if mismatch:
        st.error("❌ Images do NOT match. Possible return fraud detected!")
    else:
        st.success("✅ Images appear visually similar.")

# --------------------------------------------------------
# Step 2: Return Forecast Anomaly Detection (Prophet)
# --------------------------------------------------------
st.subheader("Step 2: Return Volume Forecasting")

uploaded_data = st.file_uploader("Upload Historical Returns CSV (ds, y)", type="csv")

if uploaded_data:
    df = pd.read_csv(uploaded_data)
    df['ds'] = pd.to_datetime(df['ds'])
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=7)
    forecast = m.predict(future)

    st.write("Forecasted Return Volume (Next 7 days):")
    st.dataframe(forecast[['ds','yhat','yhat_lower','yhat_upper']].tail(7))

    fig = m.plot(forecast)
    st.pyplot(fig)
