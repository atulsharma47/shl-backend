import streamlit as st
import pandas as pd
import requests

# Set Streamlit page config
st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")

# Load local CSV (optional)
@st.cache_data
def load_data():
    try:
        return pd.read_csv("shl_assessments.csv")
    except FileNotFoundError:
        st.warning("⚠️ 'shl_assessments.csv' not found.")
        return pd.DataFrame()

df = load_data()

# UI Header
st.title("🧠 SHL Assessment Recommender")
st.markdown("Enter a job description or relevant keyword to get assessment recommendations:")

# Input box
user_input = st.text_area("📄 Job description or keyword:", height=200)

# Button click
if st.button("🔍 Recommend Assessments"):
    if not user_input.strip():
        st.warning("Please enter something to search.")
    else:
        with st.spinner("Fetching recommendations..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/recommend",
                    headers={
                        "Content-Type": "application/json",
                        "accept": "application/json"
                    },
                    json={"query": user_input}
                )

                if response.status_code == 200:
                    data = response.json()

                    # 🔍 DEBUGGING LINE: Show raw response
                    st.write("🔎 Raw API response:", data)

                    recommendations = data.get("recommendations", [])

                    if recommendations:
                        st.success(f"✅ Found {len(recommendations)} assessment(s)")
                        st.dataframe(pd.DataFrame(recommendations))
                    else:
                        st.warning("❌ No recommendations found. Try rephrasing the job description or using clearer keywords.")
                else:
                    st.error(f"🚨 Server error: {response.status_code}")
                    st.json(response.json())

            except Exception as e:
                st.error("❌ Something went wrong while connecting to the backend.")
                st.exception(e)
