from typing import Dict, List, Any
from src.prompts import SYSTEM_PROMPT_GPTMINI_RISK, make_user_prompt_risk
from src.model_apis import get_answer_fn
from src.helpers.json_tools import safe_json_parse, fallback_payload


RISK_CATEGORIES = {
     "dosage",
    "contraindication",
    "interaction",
    "self-adjustment",
    "safety_behavior",
}
LOW_RISK_CATEGORIES = {
    "mechanism",
    "side_effects",
}

def detect_risk_gptmini(
    q_id: str,
    question_text: str,
    codes_list: List[str],
    high_stakes: bool
) -> Dict[str, Any]:
    q = question_text.strip()
    
    system_prompt = SYSTEM_PROMPT_GPTMINI_RISK
    user_prompt = make_user_prompt_risk(q_id, q, codes_list, high_stakes)
    
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    try:
        row = get_answer_fn("gptmini", full_prompt)
        parsed = safe_json_parse(row)
    except Exception:
        parsed = fallback_payload("model_call_failed")
        
    parsed.setdefault("risk_flags", ["uncertainty"])
    parsed.setdefault("risk_level", "medium")
    parsed.setdefault("evidence", [])
    parsed.setdefault("notes", "")

    return parsed