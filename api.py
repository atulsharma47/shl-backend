from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os
from fuzzywuzzy import fuzz  # Optional but useful for better matching

app = FastAPI()

# Load the CSV file
csv_path = r"C:\Users\hp\Desktop\shl-assessment-recommender\shl_assessments.csv"
df = None

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print("✅ CSV loaded successfully.")
    print("Current working directory:", os.getcwd())
    print("Normalized CSV Columns:", df.columns)
    if 'Assessment Name' in df.columns:
        print("Sample assessment names:")
        print(df['Assessment Name'].head(10))
else:
    print("❌ CSV file not found at path:", csv_path)

# Define request body using Pydantic
class Query(BaseModel):
    query: str

# Root route
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

# Recommend route
@app.post("/recommend")
def recommend_assessments(query: Query):
    if df is None:
        return {"error": "CSV file not loaded."}

    if 'Assessment Name' not in df.columns or 'Test Type' not in df.columns:
        return {"error": "Required columns not found in CSV."}

    user_query = query.query.lower()

    # Case-insensitive match using contains
    matched_df = df[
        df['Assessment Name'].str.lower().str.contains(user_query) |
        df['Test Type'].str.lower().str.contains(user_query)
    ]

    # Optional: fuzzy matching fallback if no results found
    if matched_df.empty:
        def fuzzy_match(row):
            name_score = fuzz.partial_ratio(user_query, str(row['Assessment Name']).lower())
            type_score = fuzz.partial_ratio(user_query, str(row['Test Type']).lower())
            return max(name_score, type_score)

        df["score"] = df.apply(fuzzy_match, axis=1)
        matched_df = df[df["score"] > 60].sort_values(by="score", ascending=False)

    if matched_df.empty:
        return {"message": "No assessments matched your query."}

    recommendations = matched_df.head(5).drop(columns=["score"], errors="ignore").to_dict(orient="records")
    return {"recommendations": recommendations}
