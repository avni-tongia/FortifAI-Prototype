
import streamlit as st
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from neo4j import GraphDatabase


#DeBERTa-v3
MODEL_NAME = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

#Neo4j graph database (Assuming running locally)
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))


#streamlit

st.title("✍️ Review Authenticity Detection (Phase 2)")

user_id = st.text_input("Enter User ID")
product_id = st.text_input("Enter Product ID")
review_text = st.text_area("Enter Review Text")

threshold_ai = st.slider("AI Score Threshold", 0.0, 1.0, 0.85, 0.01)
cluster_threshold = st.slider("Cluster Size Threshold", 0, 500, 50, 1)

if st.button("Analyze Review"):

    #AI model detection
    inputs = tokenizer(review_text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    probs = outputs.logits.softmax(dim=1).detach().numpy()
    ai_score = probs[0][1]
    is_ai_generated = ai_score >= threshold_ai

    st.subheader("LLM Analysis")
    st.write(f"AI-Generated Probability: {ai_score*100:.2f}%")
    st.write("Prediction:", "🚩 AI-Generated" if is_ai_generated else "✅ Human-like")

    #Neo4j coordination detection
    with driver.session() as session:
        query = (
            "MATCH (u:User)-[:REVIEWED]->(p:Product {id: $product_id}) "
            "RETURN count(u) AS num_reviewers"
        )
        result = session.run(query, product_id=product_id)
        record = result.single()
        num_reviewers = record["num_reviewers"] if record else 0

    st.subheader("Graph Coordination Analysis")
    st.write(f"Number of unique reviewers for product {product_id}: {num_reviewers}")
    is_clustered = num_reviewers >= cluster_threshold
    st.write("Cluster Status:", "🚩 Suspicious Review Cluster" if is_clustered else "✅ No Coordination Detected")

    #Final decision
    if is_ai_generated and is_clustered:
        st.error("❌ 🚩 High Risk: AI-Generated Review inside Review Cluster Detected")
    elif is_ai_generated:
        st.warning("⚠️ Review flagged as AI-generated (but no coordination detected)")
    elif is_clustered:
        st.warning("⚠️ Review cluster detected (but text seems human-like)")
    else:
        st.success("✅ Review looks legitimate")
