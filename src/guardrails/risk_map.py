from typing import Any, Dict, List

from src.guardrails.policy_codes import ReasonCode


def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip().lower() for x in value if str(x).strip()]
    return [str(value).strip().lower()]


def map_risk_to_codes(risk: Dict[str, Any] | List[str] | None) -> List[ReasonCode]:
    if not risk:
        return []

    if isinstance(risk, list):
        flags = _as_list(risk)
        intent = ""
        consequence = ""
        clinical_context = ""
    else:
        flags = _as_list(risk.get("risk_flags"))
        intent = str(risk.get("intent", "")).strip().lower()
        consequence = str(risk.get("consequence", "")).strip().lower()
        clinical_context = str(risk.get("clinical_context", "")).strip().lower()

    codes: List[ReasonCode] = []

    def add(code: ReasonCode):
        if code not in codes:
            codes.append(code)

    # context from structured fields
    if clinical_context == "pregnancy":
        add(ReasonCode.PREGNANCY_CONTEXT)
    if clinical_context in {"pediatric", "child", "children"}:
        add(ReasonCode.PEDIATRIC_CONTEXT)
    if clinical_context in {"lab", "lab_value", "inr"}:
        add(ReasonCode.LAB_VALUE_CONTEXT)

    # flags -> codes
    for flag in flags:
        if flag == "pregnancy":
            add(ReasonCode.PREGNANCY_CONTEXT)
        elif flag == "pregnancy_action":
            add(ReasonCode.PREGNANCY_ACTION)
        elif flag == "pediatric":
            add(ReasonCode.PEDIATRIC_CONTEXT)
        elif flag == "dose_request":
            add(ReasonCode.DOSE_REQUEST)
        elif flag == "side_effect_info":
            add(ReasonCode.SIDE_EFFECT_INFO)
        elif flag in {"interaction_risk", "drug_interaction", "interaction"}:
            add(ReasonCode.MEDICATION_COMBINATION)
        elif flag in {"high_risk_medication", "anticoagulant"}:
            add(ReasonCode.HIGH_RISK_MEDICATION)
        elif flag == "self_adjustment":
            add(ReasonCode.SELF_ADJUSTMENT)
        elif flag in {"needs_clinician", "supervision_needed"}:
            add(ReasonCode.NEEDS_CLINICIAN)
        elif flag in {"contraindication", "urgent_symptoms", "generic_risk"}:
            add(ReasonCode.GENERAL_RISK)
        elif flag == "uncertainty":
            # uncertainty alone should not escalate low-risk informational questions
            low_risk_info = (
                intent == "informational"
                and consequence in {"low", ""}
                and clinical_context in {"general", ""}
            )
            if not low_risk_info:
                add(ReasonCode.UNCERTAINTY)

    # structured intent/consequence fallback
    if intent == "side_effects":
        add(ReasonCode.SIDE_EFFECT_INFO)

    if intent in {"interaction_check", "interaction", "combination"}:
        add(ReasonCode.MEDICATION_COMBINATION)

    if intent in {"dose", "dosage", "dose_request"}:
        add(ReasonCode.DOSE_REQUEST)

    if intent in {"self_adjustment", "self_treatment"}:
        add(ReasonCode.SELF_ADJUSTMENT)

    if consequence == "medium" and not codes:
        add(ReasonCode.GENERAL_RISK)

    return codes