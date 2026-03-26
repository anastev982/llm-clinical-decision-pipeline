from typing import Dict, List, Tuple, Optional
from src.guardrails.policy_codes import ReasonCode, POLICY_RULES, RiskCategory
from src.helpers.types import Decision, Severity

CRITICAL_FLAGS = {"answer_contradiction", "hallucination"}

FLAG_SEVERITY: Dict[str, Severity] = {
    "answer_contradiction": Severity.HIGH,
    "hallucination": Severity.HIGH,
    "out_of_scope": Severity.HIGH,
    "missing_sources": Severity.MEDIUM,
    "overconfidence": Severity.MEDIUM,
    "answer_inconsistency": Severity.MEDIUM,
    "missing_context": Severity.MEDIUM,
}


def max_severity(flags: List[str]) -> Severity:
    order = {Severity.LOW: 0, Severity.MEDIUM: 1, Severity.HIGH: 2}
    sev = Severity.LOW
    for f in flags:
        s = FLAG_SEVERITY.get(f, Severity.LOW)
        if order[s] > order[sev]:
            sev = s
    return sev


def is_clinical(query: str) -> Tuple[bool, str]:
    query = query.lower()
    clinical_words = ["symptom", "diagnose", "dose", "therapy"]
    score = sum(1 for term in clinical_words if term in query)

    if score >= 2:
        return True, "high_confidence"
    elif score == 1:
        return True, "low_confidence"
    return False, "not_clinical"


def max_category(codes: List[ReasonCode]) -> Optional[RiskCategory]:
    order = {
        RiskCategory.LOW: 0,
        RiskCategory.MEDIUM: 1,
        RiskCategory.HIGH: 2,
        RiskCategory.HARD_STOP: 3,
    }

    best: Optional[RiskCategory] = None
    for rc in codes:
        rule = POLICY_RULES.get(rc)
        if not rule:
            continue

        cat = rule.category
        if best is None or order[cat] > order[best]:
            best = cat

    return best


def decide(
    needs_more_context: bool,
    eval_flags: List[str],
    reason_codes: List[ReasonCode],
    high_stakes: bool,
) -> tuple[Decision, Severity]:
    cat = max_category(reason_codes)

    # Gate 0: hard stop
    if cat == RiskCategory.HARD_STOP:
        return Decision.REFUSE, Severity.HIGH

    # Gate 1: missing context
    if needs_more_context:
        flags = eval_flags + ["missing_context"]
        sev = max_severity(flags)
        return (Decision.DEFER, sev) if high_stakes else (Decision.WARN, sev)

    # Gate 2: high-risk codes
    if cat == RiskCategory.HIGH:
        return Decision.ESCALATE, Severity.HIGH

    # Gate 3: medium-risk codes
    if cat == RiskCategory.MEDIUM:
        return Decision.WARN, Severity.MEDIUM

    # Gate 4: critical eval flags
    if any(f in CRITICAL_FLAGS for f in eval_flags):
        return Decision.ESCALATE, max_severity(eval_flags)

    # Gate 5: other eval flags
    if eval_flags:
        return Decision.WARN, max_severity(eval_flags)

    # Gate 6: safe default
    return Decision.ACCEPT, Severity.LOW