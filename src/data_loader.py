# src/data_loader.py
import json
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Question:
    id: str
    text: str
    category: str
    expected_elements: List[str]
    expected_decision: Optional[str] = None
    expected_severity: Optional[str] = None
    
def load_questions(filepath: str = "data/clinical_questions.json") -> List[Question]:
    """
    Loads question from json file

    Args:
        filepath (str, optional): _description_. Defaults to "data/clinical_questions.json".

    Returns:
        List[Question]: _description_.
    """
    if not filepath:
        filepath = str(Path(__file__).resolve().parents[1] / "data" / "clinical_questions.json")
    with open(filepath, 'r', encoding="utf-8") as f:
        data = json.load(f)
        
    questions = []
    for item in data:
        question = Question(
            id=item["id"],
            text=item["text"],
            category=item["category"],
            expected_elements=item.get("expected_elements", []),
            expected_decision=item.get("expected_decision"),
            expected_severity=item.get("expected_severity"),
        )
        
        questions.append(question)
        
    return questions

if __name__ == "__main__":
    questions = load_questions()
    print(f"Loaded {len(questions)} questions:")
    for q in questions:
        print(f"  {q.id}: {q.text[:50]}... ({q.category})")