from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from src.helpers.types import Decision, Severity, DecisionOutput
from src.guardrails.policy_codes import ReasonCode

@dataclass(frozen=False)
class DecisionContext:
    question_id: str
    question_text: str
    rule_reason_codes: List[ReasonCode]
    rule_audit: Dict[str, Any]
    high_stakes: bool
    llm_decision: Optional[Decision] = None
    llm_severity: Optional[Severity] = None

    
def _make_ctx(
    decision: Decision,
    severity: Severity,
    codes: List[ReasonCode],
    source: str = "policy",
    audit: Optional[Dict] = None,
) -> DecisionOutput:
    return DecisionOutput(
        decision=decision,
        severity=severity,
        reason_codes=[c.value for c in codes],
        audit=audit or {},
        source=source,
    )
    