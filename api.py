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
    try:
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()  # ✅ Clean column names
        print("✅ CSV loaded successfully.")
        print(f"CSV Shape: {df.shape}")  # Log the shape of the DataFrame
        print("CSV Columns:", df.columns)  # Log columns to ensure they are loaded correctly
        print("Sample rows:")
        print(df[['Assessment Name', 'Test Type', 'Description']].head())  # Show 'Description' too
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
else:
    print(f"❌ CSV file not found at: {csv_path}")

# ✅ Request model
class Query(BaseModel):
    query: str

# ✅ Clean up repeated or redundant phrases in the description
def clean_description(desc: str) -> str:
    print(f"clean_description IN: {desc=}")  # Debug input to clean_description
    if not desc or pd.isna(desc):  # Handle None or NaN
        print("clean_description: Returning empty string")
        return "No description available."
    desc = desc.strip()  # Strip any extra spaces
    desc = desc.replace("assessment assessment", "assessment")
    desc = desc.replace("test test", "test")
    desc = desc.replace("assessment test", "test")
    desc = desc.replace("test assessment", "assessment")
    desc = desc.replace("skills and abilities skills and abilities", "skills and abilities")
    desc = desc.replace("assessment skills and abilities assessment skills and abilities", "assessment skills and abilities")
    cleaned_desc = desc[0].upper() + desc[1:]
    print(f"clean_description OUT: {cleaned_desc=}")  # Debug output of clean_description
    return cleaned_desc

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
    print("👉 /recommend called with query:", query)  # Debug query received
    if df is None:
        print("❌ DataFrame is None!")
        return {"recommended_assessments": []}

    # Check for missing required columns
    required_columns = ['Assessment Name', 'Test Type', 'Description']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        print(f"❌ Missing required columns: {', '.join(missing_columns)}")
        return {"error": f"CSV missing required columns: {', '.join(missing_columns)}."}

    user_query = query.query.lower()

    # First try simple substring matching
    matched_df = df[
        df['Assessment Name'].str.lower().str.contains(user_query, na=False) |
        df['Test Type'].str.lower().str.contains(user_query, na=False)
    ]

    # If no match, apply keyword expansion & fuzzy matching
    if matched_df.empty:
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
            scores = [fuzz.partial_ratio(term, text) for term in expanded_terms]
            max_score = max(scores)
            print(f"Fuzzy match scores: {scores} -> Max score: {max_score}")  # Log fuzzy scores
            return max_score

        df["score"] = df.apply(fuzzy_match, axis=1)
        matched_df = df[df["score"] > 60].sort_values(by="score", ascending=False)

    if matched_df.empty:
        print("❌ No matching assessments found.")
        return {"recommended_assessments": []}

    # Format final SHL-compliant results
    results = []
    for _, row in matched_df.head(10).iterrows():
        raw_description = row.get("Description")

        # Check for empty or NaN descriptions before cleaning
        if pd.isna(raw_description) or not raw_description:
            raw_description = "No description available."

        print(f"Before clean_description: {raw_description=}")  # Log raw description before cleaning
        result = {
            "url": row.get("URL", "https://www.shl.com"),
            "adaptive_support": row.get("Adaptive Support", "No"),
            "description": clean_description(raw_description),
            "duration": int(row.get("Duration (min)", 0)),
            "remote_support": row.get("Remote Support", "No"),
            "test_type": [str(row.get("Test Type", "Other"))]
        }
        results.append(result)
        print("Result object:", result)  # Log final result object

    return {"recommended_assessments": results}
