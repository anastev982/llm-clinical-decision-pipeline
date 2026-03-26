# Rules does not change the DecisionOutput directly, but return the hits and you "pack them in".
# A pre model layer.
from typing import Callable, List, Dict, Any, Tuple
from src.guardrails.rules import RuleHit
from src.guardrails.policy_codes import ReasonCode


RuleFn = Callable[[str], List[RuleHit]]

# Aggregator - takes all the hits and transform them into reason_codes(exp. "PREGNANCY" etiquette) or audit(what rule has been triggered and why).
def apply_guardrails(
    question: str,
    rules: List[RuleFn],
    *,
    debug: bool = False
) -> Tuple[
    List[RuleHit], 
    List[ReasonCode], 
    Dict[str, Any]]:
    hits: List[RuleHit] = []

    if debug:
        print(f"[GR] rules={len(rules)} q={question[:60]!r}")

    for rule in rules:
        rule_hits = rule(question)
        if debug:
            print("[GR] rules", getattr(rule, "__name__", str(rule)), "->", rule_hits)

        if rule_hits:
            hits.extend(rule_hits)

    codes: List[ReasonCode] = [h.code for h in hits]
    audit: Dict[str, Any] = {
        "rule_hits": [
            {"code": h.code.value, "severity": h.severity, **(h.info or {})}
            for h in hits
        ]
    }

    return hits, codes, audit