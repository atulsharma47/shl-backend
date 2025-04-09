import streamlit as st
import pandas as pd
import requests

# Set page config
st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")

# Your Gemini API Key
API_KEY = "AIzaSyDX7sbxdzikBRTtwimFtTldfAqpyfU3R_4"

# Load SHL CSV
@st.cache_data
def load_data():
    try:
        return pd.read_csv("shl_assessments.csv")
    except FileNotFoundError:
        st.error("⚠️ Error: 'shl_assessments.csv' not found!")
        return pd.DataFrame()

df = load_data()

# UI
st.title("🧠 SHL Assessment Recommender")
st.markdown("Enter a job description or natural language query below:")

user_input = st.text_area("📄 Paste job description or query here:", height=200)

if st.button("🔍 Recommend Assessments"):
    if user_input.strip() == "":
        st.warning("Please enter a query or job description.")
    else:
        with st.spinner("🔄 Generating recommendations..."):

            # Gemini API request setup
            endpoint = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro-002:generateContent?key={API_KEY}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{
                    "parts": [{
                        "text": f"""
You are an AI assistant that recommends SHL assessments based on job descriptions.
Given the job description below, suggest 3-10 SHL assessments in table format:

**Query:** {user_input}

**Output format (CSV-style)**:
Assessment Name,Assessment URL,Remote Testing Support,Adaptive/IRT Support,Duration,Test Type
Example Test,https://example.com,Yes,No,30 min,Personality
"""
                    }]
                }]
            }

            # Send request to Gemini
            response = requests.post(endpoint, headers=headers, json=data)

            if response.status_code == 200:
                try:
                    reply = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                    rows = [row.strip().split(",") for row in reply.strip().split("\n") if "," in row]

                    # Ensure all rows have same length
                    max_len = max(len(r) for r in rows)
                    rows = [r + [''] * (max_len - len(r)) for r in rows]

                    df_results = pd.DataFrame(rows[1:], columns=rows[0])
                    st.markdown("### ✨ Recommended Assessments:")
                    st.dataframe(df_results)
                except Exception as e:
                    st.error(f"❌ Parsing error: {e}")
                    st.markdown("#### 🧾 Raw Response:")
                    st.code(reply)
            else:
                st.error(f"❌ API Error: {response.status_code}\n{response.text}")
