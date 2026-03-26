from src.helpers.types import Decision, Severity
from typing import Tuple
# decision_matrix.py

# 1) mapiranje consequence → Severity
CONSEQUENCE_TO_SEVERITY = {
    "low":      Severity.LOW,
    "medium":   Severity.MEDIUM,
    "high":     Severity.HIGH,
    "critical": Severity.HIGH,
}

# 2) matrica (intent, consequence) → Decision
DECISION_MATRIX = {
    ("informational", "low"):      (Decision.ACCEPT,   Severity.LOW),
    ("informational", "medium"):   (Decision.WARN,     Severity.MEDIUM),
    ("informational", "high"):     (Decision.WARN,     Severity.MEDIUM),
    ("informational", "critical"): (Decision.ESCALATE, Severity.HIGH),
    
    ("actionable", "low"):      (Decision.WARN,     Severity.MEDIUM),
    ("actionable", "medium"):   (Decision.ESCALATE, Severity.HIGH),
    ("actionable", "high"):     (Decision.ESCALATE, Severity.HIGH),
    ("actionable", "critical"): (Decision.REFUSE,   Severity.HIGH),
    
    ("self_treatment", "low"):      (Decision.WARN,     Severity.MEDIUM),
    ("self_treatment", "medium"):   (Decision.ESCALATE, Severity.HIGH),
    ("self_treatment", "high"):     (Decision.REFUSE,   Severity.HIGH),
    ("self_treatment", "critical"): (Decision.REFUSE,   Severity.HIGH),
    
    ("clarification", "low"):      (Decision.ACCEPT,   Severity.LOW),
    ("clarification", "medium"):   (Decision.ACCEPT,   Severity.LOW),
    ("clarification", "high"):     (Decision.WARN,     Severity.MEDIUM),
    ("clarification", "critical"): (Decision.ESCALATE, Severity.HIGH),
    
}

# 3) lookup funkcija
def matrix_decide(intent: str, consequence: str) -> Tuple[Decision, Severity]:
    return DECISION_MATRIX.get(
        (intent, consequence),
        (Decision.ESCALATE, Severity.HIGH)
    )