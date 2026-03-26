import json
from typing import Any, Dict

def fallback_payload(note: str) -> Dict[str, Any]:
    return {
        "risk_flags": ["uncertainty"],
        "risk_level": "medium",
        "evidence": [],
        "notes": note,
    }

def  clean_json_text(row_text: str) -> str:
    """Cleans JSON text by removing extra markdown fence and do not touch JSON symbols."""
    text = (row_text or "").strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    
    i = text.find("{")
    j = text.rfind("}")
    if i != -1 and j != -1 and j > i:
        text = text[i:j +1].strip()
        
    return text

def safe_json_parse(row_text:str) -> Dict[str, Any]:
    """Input: row text from LLM (str).
       Output: always dict. If parsing fails, fallback dict with uncertainty.
    """
    if row_text is None:
        return fallback_payload ("empty_response")
    text = row_text.strip()
    if not text:
        return fallback_payload("blank_response")
    cleaned = clean_json_text(text)
    try:
        parsed = json.loads(cleaned)
        return parsed
    except Exception as e:
        print("[DBG safe_json_parse ACTIVE]")
        print(f"JSON parse error: {e}")
        print(f"Text that failed to parse: {cleaned[:500]}")
        return fallback_payload("parse_failed")