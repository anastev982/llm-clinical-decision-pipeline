from typing import List, Tuple
import re
from src.helpers.types import Decision, Severity


#Helper func for text normalization
def normalize_models(models: List[str]) -> List[Tuple[str, str]]:
    return [(m, normalize_model(m)) for m in models]

def normalize_model(model: str) -> str:
    return re.sub(r'[-.:_\s]+', '', model.strip().lower())


# Helpers for string <-> enum 
def as_decision(x) -> Decision:
    if isinstance(x, Decision):
        return x
    return Decision(str(x))

def as_severity(x) -> Severity:
    if isinstance(x, Severity):
        return x
    return Severity(str(x))
