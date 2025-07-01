import streamlit as st
from neo4j import GraphDatabase
from datetime import datetime

st.set_page_config(page_title="Review Authenticity Detection", layout="wide")

# UPDATE THIS WITH YOUR ACTUAL NEO4J PASSWORD
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

st.title("Review Authenticity Detection")

user_id = st.text_input("User ID").strip().upper()
product_id = st.text_input("Product ID").strip().upper()
review_text = st.text_area("Review Text")

def display_card(title, content, col):
    with col:
        st.markdown(f'''
        <div style="background-color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; color: black;">
            <h4>{title}</h4>
            {content}
        </div>
        ''', unsafe_allow_html=True)

def safe_query(session, query, **params):
    try:
        result = session.run(query, **params)
        return result.single()
    except Exception as e:
        st.warning(f"Query error: {e}")
        return None

def detect_ai_patterns(text):
    ai_indicators = 0
    text_lower = text.lower()
    ai_phrases = [
        "highly recommend", "excellent product", "outstanding quality",
        "perfect for", "amazing experience", "definitely recommend",
        "great value for money", "exceeded expectations"
    ]
    for phrase in ai_phrases:
        if phrase in text_lower:
            ai_indicators += 1
    sentences = text.split('.')
    if len(sentences) > 3 and all(len(s.strip()) > 10 for s in sentences if s.strip()):
        ai_indicators += 1
    ai_score = min(ai_indicators / 5.0, 1.0)
    return ai_score

if st.button("Analyze Review") and user_id and product_id and review_text:

    with driver.session(database="neo4j") as session:
        pid_check = session.run("MATCH (p:Product {id: $pid}) RETURN p.id", pid=product_id).single()
        uid_check = session.run("MATCH (u:User {id: $uid}) RETURN u.id", uid=user_id).single()

    if not pid_check:
        st.error(f"❌ Product ID '{product_id}' not found in Neo4j.")
    if not uid_check:
        st.error(f"❌ User ID '{user_id}' not found in Neo4j.")
    if not pid_check or not uid_check:
        st.stop()

    # AI Detection (Rule-based)
    ai_score = detect_ai_patterns(review_text)
    is_ai_generated = ai_score >= 0.70

    col1, col2 = st.columns(2)
    display_card("Language Model Output", f"<b>AI-Generated Probability:</b> {ai_score * 100:.2f}%<br><b>Prediction:</b> {'AI-Generated' if is_ai_generated else 'Human-Like'}", col1)

    with driver.session(database="neo4j") as session:
        record = safe_query(session, "MATCH (u:User)-[:REVIEWED]->(p:Product {id: $product_id}) RETURN count(u) AS num_reviewers", product_id=product_id)
        num_reviewers = record["num_reviewers"] if record and "num_reviewers" in record else 0
    is_clustered = num_reviewers >= 50
    display_card("Reviewer Network Analysis", f"<b>Reviewer Count:</b> {num_reviewers}<br><b>Cluster Status:</b> {'Suspicious' if is_clustered else 'Normal'}", col2)

    with driver.session(database="neo4j") as session:
        result = session.run("MATCH (u:User)-[r:REVIEWED]->(p:Product {id: $product_id}) RETURN r.timestamp AS review_time", product_id=product_id)
        timestamps = [r["review_time"] for r in result if r["review_time"]]
    timestamp_counts = {}
    for ts in timestamps:
        ts_str = str(ts)
        timestamp_counts[ts_str] = timestamp_counts.get(ts_str, 0) + 1
    max_simultaneous = max(timestamp_counts.values()) if timestamp_counts else 0
    burst_detected = max_simultaneous >= 10
    display_card("Burst Review Check", f"<b>Reviews at same time:</b> {max_simultaneous}<br><b>Burst Status:</b> {'Detected' if burst_detected else 'Normal'}", col1)

    with driver.session(database="neo4j") as session:
        result = session.run("MATCH (u:User)-[:REVIEWED]->(p:Product {id: $product_id}) RETURN u.ip AS ip, count(*) AS count_per_ip ORDER BY count_per_ip DESC LIMIT 1", product_id=product_id)
        record = result.single()
        max_ip_count = record["count_per_ip"] if record else 0
    shared_ip_detected = max_ip_count >= 5
    display_card("IP Cluster Check", f"<b>Max reviewers from a single IP:</b> {max_ip_count}<br><b>IP Cluster Status:</b> {'Suspicious' if shared_ip_detected else 'Normal'}", col2)

    with driver.session(database="neo4j") as session:
        record = safe_query(session, "MATCH (u:User {id: $user_id})-[:REVIEWED]->(p:Product) RETURN count(p) AS review_count", user_id=user_id)
        review_count = record["review_count"] if record and "review_count" in record else 0
        reviewer_spammer = review_count >= 100
    display_card("User Review Count", f"<b>Total products reviewed:</b> {review_count}<br><b>User Activity Level:</b> {'Suspicious' if reviewer_spammer else 'Normal'}", col1)

    # Final Decision + Reasons
    reasons = []
    if is_ai_generated: reasons.append("AI-generated")
    if is_clustered: reasons.append("Reviewer cluster")
    if burst_detected: reasons.append("Review burst")
    if shared_ip_detected: reasons.append("Shared IP")
    if reviewer_spammer: reasons.append("User review spam")

    metric_list = " • ".join(["AI score", "Burst check", "Cluster count", "IP grouping", "User review count"])

    if all([is_ai_generated, is_clustered, burst_detected, shared_ip_detected]):
        st.error("High Risk: AI-generated review in a clustered, bursty, and IP-linked pattern.")
    elif reasons:
        st.warning(f"⚠️ Suspicious review flagged due to: {', '.join(reasons)}.")
    else:
        st.success("✅ Review is classified as legitimate.")

    st.caption(f"🧪 Metrics considered: {metric_list}")
