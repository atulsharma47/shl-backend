# 🧠 SHL Assessment Recommender

This project recommends SHL assessments based on job descriptions using:  
- 🔙 FastAPI backend (deployed on Render)  
- 🎨 Streamlit frontend (deployed on Streamlit Cloud)

---

## 🚀 Live App  
👉 [Open App](https://pa73owdbc2jdrpqi6icss6.streamlit.app/)

## 📘 Backend API Docs  
👉 [FastAPI Swagger UI](https://shl-fastapi.onrender.com/docs)

---

## 📊 Evaluation Metrics

To assess the recommendation quality, we used the following metrics:

- **Recall@3**: Measures how many relevant assessments were retrieved in the top 3 predictions.
- **MAP@3 (Mean Average Precision @ 3)**: Considers both relevance and ranking of assessments in the top 3.

### ✅ Evaluation Results:

Test Case Recall@3 MAP@3 0 1 0.67 0.67 1 2 0.67 0.67 2 3 0.67 0.67

Average Recall@3: 0.67
Average MAP@3: 0.67



