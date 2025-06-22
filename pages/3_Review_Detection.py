import streamlit as st
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from neo4j import GraphDatabase

st.set_page_config(
    page_title="Review Authenticity Detection",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load transformer model for review classification
MODEL_NAME = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

# Configure Neo4j database connection
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

# UI layout
st.title("Review Authenticity Detection")

user_id = st.text_input("User ID")
product_id = st.text_input("Product ID")
review_text = st.text_area("Review Text")

threshold_ai = st.slider("AI Score Threshold", 0.0, 1.0, 0.85, 0.01)
cluster_threshold = st.slider("Cluster Size Threshold", 0, 500, 50, 1)

if st.button("Analyze Review"):

    # Predict probability of review being AI-generated
    inputs = tokenizer(review_text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    probs = outputs.logits.softmax(dim=1).detach().numpy()
    ai_score = probs[0][1]
    is_ai_generated = ai_score >= threshold_ai

    st.subheader("Language Model Output")
    st.write(f"AI-Generated Probability: {ai_score * 100:.2f}%")
    st.write("Prediction:", "AI-Generated" if is_ai_generated else "Human-Like")

    # Retrieve reviewer count from Neo4j graph
    with driver.session(database="neo4j") as session:
        query = (
            "MATCH (u:User)-[:REVIEWED]->(p:Product {id: $product_id}) "
            "RETURN count(u) AS num_reviewers"
        )
        result = session.run(query, product_id=product_id)
        record = result.single()
        num_reviewers = record["num_reviewers"] if record else 0

    is_clustered = num_reviewers >= cluster_threshold

    st.subheader("Reviewer Network Analysis")
    st.write(f"Reviewer Count for Product {product_id}: {num_reviewers}")
    st.write("Cluster Status:", "Suspicious" if is_clustered else "Normal")

    # Risk decision logic
    if is_ai_generated and is_clustered:
        st.error("High Risk: AI-generated review in a suspicious cluster.")
    elif is_ai_generated:
        st.warning("Review classified as AI-generated.")
    elif is_clustered:
        st.warning("Reviewer cluster exceeds normal threshold.")
    else:
        st.success("Review is classified as legitimate.")
