import pandas as pd

# Sample test cases (Job Desc + Expected Assessments)
test_cases = [
    {
        "job_desc": "Sales Manager responsible for leading a B2B sales team",
        "expected": ["Sales Personality Test", "B2B Sales Simulation", "Leadership Potential Test"],
        "predicted": ["Leadership Potential Test", "Sales Personality Test", "Time Management Test"]
    },
    {
        "job_desc": "Software Developer with focus on Python and problem-solving",
        "expected": ["Coding Simulation - Python", "Problem Solving Test", "Logical Reasoning Test"],
        "predicted": ["Problem Solving Test", "Logical Reasoning Test", "Software Design Aptitude Test"]
    },
    {
        "job_desc": "Customer support executive for voice process",
        "expected": ["Communication Skills Test", "Customer Service Simulation", "Typing Speed Test"],
        "predicted": ["Typing Speed Test", "Communication Skills Test", "Customer Empathy Test"]
    }
]

# Metric Functions
def recall_at_k(expected, predicted, k=3):
    expected_set = set(expected)
    predicted_at_k = predicted[:k]
    correct = sum(1 for p in predicted_at_k if p in expected_set)
    return correct / len(expected_set)

def average_precision_at_k(expected, predicted, k=3):
    score = 0.0
    hits = 0
    for i, p in enumerate(predicted[:k]):
        if p in expected:
            hits += 1
            score += hits / (i + 1)
    return score / min(len(expected), k)

# Run evaluation
results = []
for i, case in enumerate(test_cases):
    recall = recall_at_k(case["expected"], case["predicted"])
    map_score = average_precision_at_k(case["expected"], case["predicted"])
    results.append({
        "Test Case": i + 1,
        "Recall@3": round(recall, 2),
        "MAP@3": round(map_score, 2)
    })

# Output results
df_results = pd.DataFrame(results)
print(df_results)
print("\nAverage Recall@3:", df_results["Recall@3"].mean())
print("Average MAP@3:", df_results["MAP@3"].mean())
