from src.flags_cross import check_numerical_contradiction, semantic_similarity

# Example results structure - replace with actual results from compare_models
results = {}

# Get answers from all models for the same question
answers = [
    results["gemini"]["answer"],
    results["deepseek"]["answer"],
    results["gpt-4"]["answer"],
    results['CoPilot']['answer'],
    results['Perplexity']['answer']
]

# Check if they agree (already have in flags_cross.py)
contradictions = check_numerical_contradiction(answers)
similarity = semantic_similarity(answers[0], answers[1])