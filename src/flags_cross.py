from typing import List, Tuple, Optional
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from numpy import dot
from numpy.linalg import norm

_model = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all_miniLM-L6-v2')
    return _model


CROSS_Q_FLAGS = {
    "answer_inconsistency": {
        "severity": "high",
        "description": "Semantically different answers given to equivalent or paraphrased questions."
    },
    "answer_contradiction": {
        "severity": "high",
        "description": "Conflicting signals (e.g., allow vs prohibit) appear across answers to equivalent prompts."
    },
    "confidence_flip": {
        "severity": "high",
        "description": "Model confidence changes significantly across equivalent prompts."
    },
    "selective_caution": {
        "severity": "medium",
        "description": "Model requests clarification or expresses uncertainty inconsistently across prompts."
    },
    "escalation_instability": {
        "severity": "high",
        "description": "Human escalation decision is not stable across equivalent inputs."
    }
}


def extract_numbers(text: str) -> List[Tuple[str, float]]:
    pattern = r'(\d+(?:\.\d+)?)\s*(mg|ml|kg|%)'
    return [(unit, float(val)) for val, unit in re.findall(pattern, text)]

def check_numerical_contradiction(answers: List[str]) -> Optional[str]:
    all_nums = [extract_numbers(a) for a in answers]
    # If the same unit has different values
    for unit in set(u for nums in all_nums for u, _ in nums):
        values = set(v for nums in all_nums for u, v in nums if u == unit)
        if len(values) > 1:
            return f"CONTRADICTION_{unit}"
    return None

def semantic_similarity(ans1: str, ans2: str) -> float:
    model = get_model()
    e1, e2 = model.encode([ans1, ans2])
    return dot(e1, e2) / (norm(e1) * norm(e2))
