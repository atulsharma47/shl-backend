from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os
from fuzzywuzzy import fuzz

app = FastAPI()

# Load CSV
csv_path = r"C:\Users\hp\Desktop\shl-assessment-recommender\shl_assessments.csv"
df = None

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print("✅ CSV loaded successfully.")
    print("Current working directory:", os.getcwd())
    print("CSV Columns:", df.columns)
else:
    print("❌ CSV file not found at:", csv_path)

# Request body model
class Query(BaseModel):
    query: str

# ✅ Health Check Endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Root route (optional, kept for context)
@app.get("/")
def read_root():
    return {
        "message": "🎉 Welcome to the SHL Assessment Recommender API!",
        "usage": "Use the /recommend endpoint with a POST request.",
        "example": {
            "endpoint": "/recommend",
            "method": "POST",
            "body": {
                "query": "Cognitive"
            }
        }
    }

# ✅ SHL-Compliant Recommend Endpoint
@app.post("/recommend")
def recommend_assessments(query: Query):
    if df is None:
        return {"recommended_assessments": []}

    if 'Assessment Name' not in df.columns:
        return {"error": "Assessment Name column missing from CSV."}

    user_query = query.query.lower()

    # Basic matching
    matched_df = df[
        df['Assessment Name'].str.lower().str.contains(user_query) |
        df['Test Type'].str.lower().str.contains(user_query)
    ]

    # Fuzzy fallback
    if matched_df.empty:
        def fuzzy_match(row):
            name_score = fuzz.partial_ratio(user_query, str(row['Assessment Name']).lower())
            type_score = fuzz.partial_ratio(user_query, str(row.get('Test Type', '')).lower())
            return max(name_score, type_score)

        df["score"] = df.apply(fuzzy_match, axis=1)
        matched_df = df[df["score"] > 60].sort_values(by="score", ascending=False)

    if matched_df.empty:
        return {"recommended_assessments": []}

    results = []

    for _, row in matched_df.head(10).iterrows():
        result = {
            "url": row.get("URL", "https://www.shl.com"),
            "adaptive_support": row.get("Adaptive Support", "No"),
            "description": row.get("Description", "No description available."),
            "duration": int(row.get("Duration (min)", 0)),
            "remote_support": row.get("Remote Support", "No"),
            "test_type": [str(row.get("Test Type", "Other"))]
        }
        results.append(result)

    return {"recommended_assessments": results}
