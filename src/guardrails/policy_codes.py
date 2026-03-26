from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

from src.helpers.types import Decision, Severity


class RiskCategory(str, Enum):
    HARD_STOP = "HARD_STOP"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ReasonCode(str, Enum):
    DOSE_REQUEST = "DOSE_REQUEST"
    MEDICATION_COMBINATION = "MEDICATION_COMBINATION"
    SELF_ADJUSTMENT = "SELF_ADJUSTMENT"

    PREGNANCY_CONTEXT = "PREGNANCY_CONTEXT"
    PEDIATRIC_CONTEXT = "PEDIATRIC_CONTEXT"
    LAB_VALUE_CONTEXT = "LAB_VALUE_CONTEXT"

    HIGH_RISK_MEDICATION = "HIGH_RISK_MEDICATION"
    NEEDS_CLINICIAN = "NEEDS_CLINICIAN"
    SIDE_EFFECT_INFO = "SIDE_EFFECT_INFO"
    GENERAL_RISK = "GENERAL_RISK"
    UNCERTAINTY = "UNCERTAINTY"

    INSULIN_UNSUPERVISED = "INSULIN_UNSUPERVISED"
    PREGNANCY_ACTION = "PREGNANCY_ACTION"
    WARFARIN_INR_DOSING = "WARFARIN_INR_DOSING"

@dataclass(frozen=True)
class PolicyRule:
    category: RiskCategory
    decision: Decision
    severity: Severity
    safe_msg: Optional[str] = None


POLICY_RULES: Dict[ReasonCode, PolicyRule] = {
    ReasonCode.INSULIN_UNSUPERVISED: PolicyRule(
        category=RiskCategory.HARD_STOP,
        decision=Decision.REFUSE,
        severity=Severity.HIGH,
        safe_msg="I can't help with insulin dose adjustment without medical supervision. Please contact your clinician."
    ),
    ReasonCode.PREGNANCY_ACTION: PolicyRule(
        category=RiskCategory.HARD_STOP,
        decision=Decision.REFUSE,
        severity=Severity.HIGH,
        safe_msg="I can't provide actionable medication advice during pregnancy. Please contact your clinician."
    ),
    ReasonCode.WARFARIN_INR_DOSING: PolicyRule(
        category=RiskCategory.HARD_STOP,
        decision=Decision.REFUSE,
        severity=Severity.HIGH,
        safe_msg="I can't provide warfarin dose adjustment based on INR. Please contact your clinician."
    ),

    ReasonCode.DOSE_REQUEST: PolicyRule(
        category=RiskCategory.HIGH,
        decision=Decision.ESCALATE,
        severity=Severity.HIGH,
        safe_msg=None
    ),
    ReasonCode.MEDICATION_COMBINATION: PolicyRule(
        category=RiskCategory.HIGH,
        decision=Decision.ESCALATE,
        severity=Severity.HIGH,
        safe_msg=None
    ),
    ReasonCode.SELF_ADJUSTMENT: PolicyRule(
        category=RiskCategory.HIGH,
        decision=Decision.ESCALATE,
        severity=Severity.HIGH,
        safe_msg=None
    ),

    ReasonCode.PREGNANCY_CONTEXT: PolicyRule(
        category=RiskCategory.HIGH,
        decision=Decision.ESCALATE,
        severity=Severity.HIGH,
        safe_msg="Medication questions in pregnancy require clinician review."
    ),
    ReasonCode.PEDIATRIC_CONTEXT: PolicyRule(
        category=RiskCategory.HIGH,
        decision=Decision.ESCALATE,
        severity=Severity.HIGH,
        safe_msg="Medication questions for children require clinician review."
    ),
    ReasonCode.LAB_VALUE_CONTEXT: PolicyRule(
        category=RiskCategory.HIGH,
        decision=Decision.ESCALATE,
        severity=Severity.HIGH,
        safe_msg="Medication advice based on lab values requires clinician review."
    ),
    ReasonCode.HIGH_RISK_MEDICATION: PolicyRule(
        category=RiskCategory.HIGH,
        decision=Decision.ESCALATE,
        severity=Severity.HIGH,
        safe_msg="High-risk medication questions require clinician review."
    ),

    ReasonCode.NEEDS_CLINICIAN: PolicyRule(
        category=RiskCategory.MEDIUM,
        decision=Decision.DEFER,
        severity=Severity.MEDIUM,
        safe_msg=None
    ),
    ReasonCode.SIDE_EFFECT_INFO: PolicyRule(
        category=RiskCategory.MEDIUM,
        decision=Decision.WARN,
        severity=Severity.MEDIUM,
        safe_msg=None
    ),
    ReasonCode.GENERAL_RISK: PolicyRule(
        category=RiskCategory.MEDIUM,
        decision=Decision.WARN,
        severity=Severity.MEDIUM,
        safe_msg=None
    ),
    ReasonCode.UNCERTAINTY: PolicyRule(
        category=RiskCategory.LOW,
        decision=Decision.WARN,
        severity=Severity.MEDIUM,
        safe_msg=None
    ),
}

def is_hard_stop(code: ReasonCode) -> bool:
    rule = POLICY_RULES.get(code)
    return bool(rule and rule.category == RiskCategory.HARD_STOP)


def hard_stop_msg(codes: List[ReasonCode]) -> Optional[str]:
    for code in codes:
        rule = POLICY_RULES.get(code)
        if rule and rule.category == RiskCategory.HARD_STOP:
            return rule.safe_msg
    return None