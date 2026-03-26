from dataclasses import dataclass, field
from typing import List

# Middle layer in transition from label_based in feature_based design
@dataclass
class RiskProfile:
    intents: List[str] = field(default_factory=list)
    contexts: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    confidence: str = "low"