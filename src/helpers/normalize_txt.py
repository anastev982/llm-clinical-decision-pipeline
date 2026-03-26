import re

    
def normalize_text(t: str) -> str:
    t = t.lower()
    t = re.sub(r"\b1st\b", "first", t)
    t = re.sub(r"\b2nd\b", "second", t)
    t = re.sub(r"\b3rd\b", "third", t)
    t = re.sub(r"\b(wk|wks)\b", "weeks", t)
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()