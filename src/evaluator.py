# This file's content has been moved to risk_flags_cross.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from src.risk_flags_cross import detect_cross_answer_flags

@dataclass
class EvaluationResult:
    question_id: str
    flags: List[str]
    notes: List[str]
    metrics: List[str]
    
def _clean_answer(answers: List[str]) -> List[str]:
    return [a.strip() for a in answers if a and a.strip()]
    
def evaluate_answers(
    question_id: str,
    answers: List[str],
    *,
    question_text: Optional[str] = None,
    model_name: Optional[str] = None,
    risk_level: Optional[str] = None,
) -> EvaluationResult:
    # This is for signal extraction only. No decisions.
    
    clean = _clean_answer(answers)
    n = len(clean)
    
    notes = (
        ["No non-empty answers provided"] if n == 0
        else ["Only one answer provided, cross-answer stability can not be measured."] if n == 1
        else []
    )
    
    flags = ["No answer"] if n == 0 else detect_cross_answer_flags(clean)
    
    return EvaluationResult(
        question_id=question_id,
        flags=flags,
        notes=notes,
        metrics=[]
    )