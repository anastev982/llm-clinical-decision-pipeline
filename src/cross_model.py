# Calculate consensus - % passed models
# Detect congtradiction (diferent decision mellom valid answers)
# Pics best ModelResult (least "bad", most useful)

from collections import Counter
from typing import Dict, Tuple, Optional, List, Any
from src.guardrails.policy_codes import ReasonCode, is_hard_stop
from src.helpers.types import (
    ModelResult, 
    CrossModelAnalysis, 
    SingleQuestionResult,
    Decision,
    Severity
)


 # A threshold - pre-policy
def pre_policy_from_cross_model(
    cross: CrossModelAnalysis,
    high_stakes: bool,
) -> Tuple[Optional[Decision], Optional[Severity]]:
    # If there is nothing valid
    if cross.contradictions and "no_valid_results" in cross.contradictions:
        return (Decision.ESCALATE, Severity.HIGH) if high_stakes else (Decision.DEFER, Severity.HIGH)

    # If there is no clear majority in decision
    if getattr(cross, "decision_consensus", 0.0) < 0.60:
        return Decision.ESCALATE, Severity.HIGH

    # If just a few pass on quality 
    if cross.consensus < 0.60:
        return (Decision.ESCALATE, Severity.HIGH) if high_stakes else (Decision.WARN, Severity.MEDIUM)

    # OK: let the best model lead
    return None, None   # signal: "no override"


# Helper
def _sev_rank(sev: Severity) -> int:
    order = {Severity.LOW: 0, Severity.MEDIUM: 1, Severity.HIGH: 2}
    return order.get(sev, 99)

def _dec_rank(dec: Decision) -> int:
    order = {
        Decision.ACCEPT: 0,
        Decision.WARN: 1,
        Decision.DEFER: 2,
        Decision.ESCALATE: 3,
        Decision.REFUSE: 4,
    }
    return order.get(dec, 99)


def compute_cross_model(model_results: Dict[str, ModelResult]) -> CrossModelAnalysis:
    valid: List[Tuple[str, ModelResult]] = [
        (k, r) for k, r in model_results.items()
        if r is not None and r.decision and r.decision != Decision.ERROR
    ]
    if not valid:
        return CrossModelAnalysis(
            contradictions=["no_valid_results"],
            avg_similarity=0.0,
            consensus=0.0,              # passed_consensus
            decision_consensus=0.0,
        )

    # 1) passed_consensus = % modela koji su passed
    passed_count = sum(1 for _, r in valid if bool(r.passed))
    passed_consensus = passed_count / len(valid)

    # 2) decision_consensus = % modela koji podržava najčešću odluku
    decisions = [r.decision for _, r in valid]
    dist = Counter(decisions)
    top_count = max(dist.values()) if dist else 0
    decision_consensus = top_count / len(valid)

    # 3) contradictions = samo ako postoji više različitih odluka
    contradictions: Optional[List[str]] = None
    if len(dist) > 1:
        contradictions = [f"decision_split: {dict(dist)}"]

    return CrossModelAnalysis(
        contradictions=contradictions,
        avg_similarity=0.0,
        consensus=passed_consensus,
        decision_consensus=decision_consensus,
    )
        

def select_best_model_result(model_results: Dict[str, ModelResult]) -> Optional[Tuple[str, ModelResult]]:
    valid = [
        (k, r) for k, r in model_results.items()
        if r is not None and r.decision and r.decision != Decision.ERROR
    ]
    if not valid:
        return None
    
    def score(item:Tuple[str, ModelResult]):
        _, r = item
        return (
            0 if r.passed else 1,
            _sev_rank(r.severity),
            0 if (r.answer and r.answer.strip()) else 1,
        )
    return min(valid, key=score)



def pick_stricter(a: Tuple[Decision, Severity], b: Tuple[Decision, Severity]) -> Tuple[Decision, Severity]:
    # strožija decision pobeđuje; ako su iste, veća severity pobeđuje
    da, sa = a
    db, sb = b

    if _dec_rank(db) > _dec_rank(da):
        return b
    if _dec_rank(db) < _dec_rank(da):
        return a
    return b if _sev_rank(sb) > _sev_rank(sa) else a


# 2) Hard stop + bump iz reason_codes (policy sloj)

def policy_override_from_reason_codes(
    reason_codes: List[ReasonCode]
    ) -> Tuple[Optional[str], Optional[Tuple[Decision, Severity]]]:
    codes = set(reason_codes or [])

    # HARD STOP primeri
    if any(is_hard_stop(c) for c in codes):
        return "hard_stop_triggered", (Decision.REFUSE, Severity.HIGH)

    # BUMP primeri
    BUMP_TO_ESCALATE = {
        ReasonCode.DOSE_REQUEST, 
        ReasonCode.INSULIN_UNSUPERVISED, 
        ReasonCode.WARFARIN_INR_DOSING
        }
    
    if codes & BUMP_TO_ESCALATE:
        return None, (Decision.ESCALATE, Severity.HIGH)

    return None, None

# 3) Kombinovanje: pre-policy + policy = final

def combine_pre_policy_and_policy(
    pre_decision: Decision,
    pre_severity: Severity,
    reason_codes: List[ReasonCode],
) -> Tuple[Decision, Severity, Dict[str, Any]]:
    audit: Dict[str, Any] = {
        "pre_policy": {"decision": pre_decision.value, "severity": pre_severity.value},
        "reason_codes": [c.value for c in (reason_codes or [])],
    }

    hard_msg, override = policy_override_from_reason_codes(reason_codes)

    if override is not None:
        final_dec, final_sev = pick_stricter((pre_decision, pre_severity), override)
        audit["policy"] = {
            "override": {"decision": override[0].value, "severity": override[1].value},
            "hard_stop": bool(hard_msg)
            }
        audit["final"] = {"decision": final_dec.value, "severity": final_sev.value}
        return final_dec, final_sev, audit

    audit["policy"] = {"override": None, "hard_stop": False}
    audit["final"] = {"decision": pre_decision.value, "severity": pre_severity.value}
    return pre_decision, pre_severity, audit


# Make cross_models report
# Pick and mark best candidate (one result that serves as a basis)
def enrich_single_question_result(
    sqr: SingleQuestionResult,
    high_stakes: bool = False,
    reason_codes: Optional[List[ReasonCode]] = None,
) -> None:
    sqr.cross_model = compute_cross_model(sqr.model_results)
    
    best = select_best_model_result(sqr.model_results)
    if best is None:
        return

    best_key, best_res = best
    best_res.audit = best_res.audit or {}
    best_res.audit["best_selected"] = True
    best_res.audit["best_selected_key"] = best_key
    
    override_dec, override_sev = pre_policy_from_cross_model(sqr.cross_model, high_stakes)

    if override_dec is not None and override_sev is not None:
        pre_decision, pre_severity = override_dec, override_sev
    else:
        pre_decision, pre_severity = best_res.decision, best_res.severity

    # Save pre-policy in audit
    best_res.audit["pre_policy"] = {
        "decision": pre_decision.value if hasattr(pre_decision, 'value') else pre_decision,
        "severity": pre_severity.value if hasattr(pre_severity, 'value') else pre_severity,
        }

    # If you have reason_codes, do final merge (policy has final say)
    if reason_codes is not None:
        final_dec, final_sev, merge_audit = combine_pre_policy_and_policy(
            pre_decision=pre_decision,
            pre_severity=pre_severity,
            reason_codes=reason_codes,
        )
        best_res.audit["final_merge"] = merge_audit
        best_res.audit["final_decision"] = final_dec
        best_res.audit["final_severity"] = final_sev