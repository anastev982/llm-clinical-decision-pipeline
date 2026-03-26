from typing import Iterable, List, Tuple

from src.guardrails.policy_codes import POLICY_RULES, ReasonCode, is_hard_stop
from src.helpers.types import Decision, Severity


DecisionPair = Tuple[Decision, Severity]


def _uniq(codes: Iterable[ReasonCode]) -> List[ReasonCode]:
    seen = set()
    out = []
    for code in codes:
        if code not in seen:
            seen.add(code)
            out.append(code)
    return out


def _has(codes: set[ReasonCode], *need: ReasonCode) -> bool:
    return all(code in codes for code in need)


def _pick(rule_code: ReasonCode) -> DecisionPair:
    rule = POLICY_RULES[rule_code]
    return rule.decision, rule.severity


def _fallback_from_rules(codes: List[ReasonCode]) -> DecisionPair:
    ranked = [POLICY_RULES[c] for c in codes if c in POLICY_RULES]
    if not ranked:
        return Decision.ACCEPT, Severity.LOW

    order = {Severity.LOW: 0, Severity.MEDIUM: 1, Severity.HIGH: 2}
    ranked.sort(key=lambda r: order[r.severity], reverse=True)
    top = ranked[0]
    return top.decision, top.severity


def decide_from_reason_codes(
    reason_codes: Iterable[ReasonCode],
    *,
    high_stakes: bool,
) -> DecisionPair:
    codes = _uniq(reason_codes)
    c = set(codes)

    # 1. hard stops
    for code in codes:
        if is_hard_stop(code):
            return _pick(code)

    # 2. uncertainty alone should not block low-risk info
    if c == {ReasonCode.UNCERTAINTY} and not high_stakes:
        return Decision.ACCEPT, Severity.LOW

    # 3. strongest combinations
    if _has(c, ReasonCode.DOSE_REQUEST, ReasonCode.PREGNANCY_CONTEXT):
        return Decision.ESCALATE, Severity.HIGH

    if _has(c, ReasonCode.DOSE_REQUEST, ReasonCode.PEDIATRIC_CONTEXT):
        return Decision.ESCALATE, Severity.HIGH

    if _has(c, ReasonCode.DOSE_REQUEST, ReasonCode.LAB_VALUE_CONTEXT):
        return Decision.ESCALATE, Severity.HIGH

    if _has(c, ReasonCode.DOSE_REQUEST, ReasonCode.MEDICATION_COMBINATION):
        return Decision.ESCALATE, Severity.HIGH

    if _has(c, ReasonCode.SELF_ADJUSTMENT, ReasonCode.HIGH_RISK_MEDICATION):
        return Decision.ESCALATE, Severity.HIGH

    # 4. softer informational routes
    if ReasonCode.SIDE_EFFECT_INFO in c:
        return Decision.WARN, Severity.MEDIUM

    if ReasonCode.NEEDS_CLINICIAN in c:
        return Decision.DEFER, Severity.MEDIUM

    # 5. generic dose logic
    # high-risk medication dose question without INR/self-adjustment -> DEFER
    if ReasonCode.DOSE_REQUEST in c:
        if ReasonCode.HIGH_RISK_MEDICATION in c:
            return Decision.DEFER, Severity.MEDIUM
        return Decision.DEFER, Severity.MEDIUM

    # 6. informational interaction/combination without stronger context
    if ReasonCode.MEDICATION_COMBINATION in c:
        return Decision.WARN, Severity.MEDIUM

    # 7. fallback
    return _fallback_from_rules(codes)