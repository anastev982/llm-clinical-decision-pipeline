import re
from typing import List

from src.helpers.types import RuleHit
from src.guardrails.policy_codes import ReasonCode
from src.helpers.normalize_txt import normalize_text
from src.guardrails.regex import PREG_RE, ACTION_RE
from src.helpers.json_tools import safe_json_parse, fallback_payload
from src.prompts import SYSTEM_PROMPT_GPTMINI_RISK
from src.model_apis import get_answer_fn


DOSE_RE = re.compile(
    r"\b("
    r"dose|dosage|mg|ml|how much|how many|how often|"
    r"take tonight|should i take|can i take|"
    r"alternate|alternating|stagger|switch between|"
    r"every\s+\d+\s*(hour|hours|hr|hrs)|"
    r"\d+\s*(mg|ml)"
    r")\b",
    re.I,
)

SIDE_EFFECT_RE = re.compile(
    r"\b(side effect|side effects|adverse effect|adverse effects)\b",
    re.I,
)

COMBINATION_RE = re.compile(
    r"\b("
    r"together|combine|combined|mix|mixed|"
    r"alternate|alternating|stagger|switch between|"
    r"interact|interaction|safe to take together"
    r")\b",
    re.I,
)

SELF_ADJUST_RE = re.compile(
    r"\b("
    r"adjust my|change my|increase my|decrease my|"
    r"stop my|restart my|on my own|myself|without supervision"
    r")\b",
    re.I,
)

PEDIATRIC_RE = re.compile(
    r"\b(child|children|kid|5-year-old|year-old|pediatric|infant|baby)\b",
    re.I,
)

LAB_VALUE_RE = re.compile(
    r"\b(inr|creatinine|egfr|a1c|hba1c|glucose)\b",
    re.I,
)

HIGH_RISK_MEDS_RE = re.compile(
    r"\b(warfarin|insulin)\b",
    re.I,
)

FLAG_MAP = {
    "dose_request": ReasonCode.DOSE_REQUEST,
    "pregnancy": ReasonCode.PREGNANCY_CONTEXT,
    "pregnancy_action": ReasonCode.PREGNANCY_ACTION,
    "pediatric": ReasonCode.PEDIATRIC_CONTEXT,
    "interaction_risk": ReasonCode.MEDICATION_COMBINATION,
    "anticoagulant": ReasonCode.HIGH_RISK_MEDICATION,
    "high_risk_medication": ReasonCode.HIGH_RISK_MEDICATION,
    "self_adjustment": ReasonCode.SELF_ADJUSTMENT,
    "supervision_needed": ReasonCode.NEEDS_CLINICIAN,
    "needs_clinician": ReasonCode.NEEDS_CLINICIAN,
    "contraindication": ReasonCode.GENERAL_RISK,
    "urgent_symptoms": ReasonCode.GENERAL_RISK,
    "side_effect_info": ReasonCode.SIDE_EFFECT_INFO,
    "uncertainty": ReasonCode.UNCERTAINTY,
}

def rule_side_effect_info(question: str) -> List[RuleHit]:
    return _hit_if(SIDE_EFFECT_RE, question, ReasonCode.SIDE_EFFECT_INFO, "side_effects", severity="medium")

def _q(question: str) -> str:
    return normalize_text(question)


def _hit(code: ReasonCode, pattern: str, severity: str = "high") -> List[RuleHit]:
    return [RuleHit(code=code, severity=severity, info={"pattern": pattern})]


def _hit_if(regex, question: str, code: ReasonCode, pattern: str, severity: str = "high") -> List[RuleHit]:
    return _hit(code, pattern, severity) if regex.search(_q(question)) else []


def rule_dose_request(question: str) -> List[RuleHit]:
    return _hit_if(DOSE_RE, question, ReasonCode.DOSE_REQUEST, "dose")


def rule_medication_combination(question: str) -> List[RuleHit]:
    return _hit_if(COMBINATION_RE, question, ReasonCode.MEDICATION_COMBINATION, "combination")


def rule_self_adjustment(question: str) -> List[RuleHit]:
    return _hit_if(SELF_ADJUST_RE, question, ReasonCode.SELF_ADJUSTMENT, "self_adjustment")


def rule_pregnancy_action(question: str) -> List[RuleHit]:
    q = _q(question)
    return _hit(ReasonCode.PREGNANCY_ACTION, "pregnancy+action") if PREG_RE.search(q) and ACTION_RE.search(q) else []


def rule_pregnancy_context(question: str) -> List[RuleHit]:
    return _hit_if(PREG_RE, question, ReasonCode.PREGNANCY_CONTEXT, "pregnancy")


def rule_pediatric_context(question: str) -> List[RuleHit]:
    return _hit_if(PEDIATRIC_RE, question, ReasonCode.PEDIATRIC_CONTEXT, "pediatric")


def rule_lab_value_context(question: str) -> List[RuleHit]:
    return _hit_if(LAB_VALUE_RE, question, ReasonCode.LAB_VALUE_CONTEXT, "lab_value")


def rule_high_risk_medication(question: str) -> List[RuleHit]:
    return _hit_if(HIGH_RISK_MEDS_RE, question, ReasonCode.HIGH_RISK_MEDICATION, "high_risk_med")


def rule_insulin_without_supervision(question: str) -> List[RuleHit]:
    q = _q(question)
    if "insulin" in q and ("without supervision" in q or "adjust my" in q or "myself" in q):
        return _hit(ReasonCode.INSULIN_UNSUPERVISED, "insulin_unsupervised")
    return []


def rule_warfarin_inr_dosing(question: str) -> List[RuleHit]:
    q = _q(question)
    if "warfarin" in q and "inr" in q and re.search(r"\b\d+(\.\d+)?\b", q) and DOSE_RE.search(q):
        return _hit(ReasonCode.WARFARIN_INR_DOSING, "warfarin+inr+dose")
    return []


def rule_llm_classifier(question: str, model: str) -> List[RuleHit]:
    try:
        raw = get_answer_fn(model, f"{SYSTEM_PROMPT_GPTMINI_RISK}\n\nUser question:\n{question}")
        parsed = safe_json_parse(raw)
    except Exception:
        parsed = fallback_payload("model_call_failed")

    flags = parsed.get("risk_flags") or ["uncertainty"]
    evidence = parsed.get("evidence") or []
    severity = str(parsed.get("risk_level", "medium")).lower()

    hits = []
    for i, flag in enumerate(flags):
        code = FLAG_MAP.get(str(flag).strip().lower(), ReasonCode.UNCERTAINTY)
        hits.append(
            RuleHit(
                code=code,
                severity=severity,
                info={
                    "flag": flag,
                    "evidence": evidence[i] if i < len(evidence) else f"llm_flag={flag}",
                    "source": "llm",
                },
            )
        )
    return hits


RULES = [
    rule_pregnancy_action,
    rule_warfarin_inr_dosing,
    rule_insulin_without_supervision,
    rule_side_effect_info,
    rule_dose_request,
    rule_medication_combination,
    rule_self_adjustment,
    rule_pregnancy_context,
    rule_pediatric_context,
    rule_lab_value_context,
    rule_high_risk_medication,
]