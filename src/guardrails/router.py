from typing import Iterable, Optional, Tuple

from src.helpers.types import Decision, Severity
from src.guardrails.policy_codes import ReasonCode


Route = Tuple[Decision, Severity, str | None]


def _has(codes: set[ReasonCode], *need: ReasonCode) -> bool:
    return all(code in codes for code in need)


def _route(decision: Decision, severity: Severity, msg: str | None = None) -> Route:
    return decision, severity, msg


def guardrail_route(codes: Iterable[ReasonCode]) -> Optional[Route]:
    c = set(codes)

    hard_stops = {
        ReasonCode.INSULIN_UNSUPERVISED: "Insulin dose adjustment requires clinician supervision.",
        ReasonCode.PREGNANCY_ACTION: "Actionable medication advice during pregnancy requires clinician review.",
        ReasonCode.WARFARIN_INR_DOSING: "Warfarin dose adjustment based on INR requires clinician review.",
    }

    for code, msg in hard_stops.items():
        if code in c:
            return _route(Decision.REFUSE, Severity.HIGH, msg)

    escalate_patterns = [
        (ReasonCode.DOSE_REQUEST, ReasonCode.PREGNANCY_CONTEXT),
        (ReasonCode.DOSE_REQUEST, ReasonCode.PEDIATRIC_CONTEXT),
        (ReasonCode.DOSE_REQUEST, ReasonCode.LAB_VALUE_CONTEXT),
        (ReasonCode.MEDICATION_COMBINATION, ReasonCode.HIGH_RISK_MEDICATION),
        (ReasonCode.SELF_ADJUSTMENT, ReasonCode.HIGH_RISK_MEDICATION),
    ]

    if any(_has(c, *pattern) for pattern in escalate_patterns):
        return _route(Decision.ESCALATE, Severity.HIGH)

    return None