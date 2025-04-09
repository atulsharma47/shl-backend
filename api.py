from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os
from fuzzywuzzy import fuzz

app = FastAPI()

# ✅ Use relative path so it works on Render & locally
csv_path = os.path.join(os.path.dirname(__file__), "shl_assessments.csv")
df = None

# ✅ Load CSV with validation
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print("✅ CSV loaded successfully.")
    print("Sample rows:")
    print(df[['Assessment Name', 'Test Type']].head())
else:
    print(f"❌ CSV file not found at: {csv_path}")

# ✅ Request model
class Query(BaseModel):
    query: str

# ✅ Health Check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ✅ Root route
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

# ✅ Recommend assessments
@app.post("/recommend")
def recommend_assessments(query: Query):
    if df is None:
        return {"recommended_assessments": []}

    if 'Assessment Name' not in df.columns or 'Test Type' not in df.columns:
        return {"error": "CSV missing required columns."}

    user_query = query.query.lower()

    # ✅ First try simple substring matching
    matched_df = df[
        df['Assessment Name'].str.lower().str.contains(user_query, na=False) |
        df['Test Type'].str.lower().str.contains(user_query, na=False)
    ]

    # ✅ If no match, apply keyword expansion & fuzzy matching
    if matched_df.empty:
        # Expand keywords based on common synonyms
        extra_keywords = {
            "coding": ["programming", "developer", "test", "technical"],
            "python": ["coding", "scripting"],
            "data": ["analysis", "analytics"],
            "reasoning": ["logic", "verbal", "numerical"],
        }

        query_keywords = user_query.split()
        expanded_terms = query_keywords.copy()
        for word in query_keywords:
            expanded_terms += extra_keywords.get(word, [])

        def fuzzy_match(row):
            text = f"{row['Assessment Name']} {row.get('Test Type', '')}".lower()
            return max(fuzz.partial_ratio(term, text) for term in expanded_terms)

        df["score"] = df.apply(fuzzy_match, axis=1)
        matched_df = df[df["score"] > 60].sort_values(by="score", ascending=False)

    if matched_df.empty:
        return {"recommended_assessments": []}

    # ✅ Format final SHL-compliant results
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
