from typing import List
from src.guardrails.policy_codes import ReasonCode
from src.guardrails.risk_profile import RiskProfile

def build_risk_profile(question_text: str, reason_codes: List[ReasonCode]) -> RiskProfile:
    profile = RiskProfile()
    
    for code in reason_codes:
        if code == ReasonCode.DOSE_REQUEST:
            profile.intents.append("DOSE_REQUEST")
        elif code == ReasonCode.PREGNANCY:
            profile.contexts.append("PREGNANCY")
        elif code == ReasonCode.PREGNANCY_ACTION:
            profile.intents.append("MED_CHANGE")
            profile.contexts.append("PREGNANCY")
        elif code == ReasonCode.PEDIATRIC_DOSING:
            profile.intents.append("DOSE_REQUEST")
            profile.contexts.append("PEDIATRIC")

    return profile