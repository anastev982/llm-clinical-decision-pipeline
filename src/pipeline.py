from typing import Any, Dict, List, Optional

from src.evaluator import evaluate_answers
from src.guardrails.decision_policy import decide_from_reason_codes
from src.guardrails.policy_codes import ReasonCode
from src.helpers.types import Decision, Severity, DecisionOutput
from src.helpers.decision_ctx import DecisionContext, _make_ctx
from src.helpers.debug import dbg, codes_to_str


def is_high_stakes(question: str) -> bool:
    q = question.lower()
    triggers = [
        "dose", "dosage", "how much", "mg", "ml",
        "5-year-old", "child", "pregnant", "warfarin", "insulin",
        "without medical supervision", "together without consulting"
    ]
    return any(t in q for t in triggers)


def decide_one(ctx: DecisionContext, *, model_name: str, answer: str) -> DecisionOutput:
    return make_decision(
        question_id=ctx.question_id,
        answers=[answer],
        model_name=model_name,
        question_text=ctx.question_text,
        rule_reason_codes=ctx.rule_reason_codes,
        rule_audit=ctx.rule_audit,
        high_stakes=ctx.high_stakes,
    )


def make_decision(
    *,
    question_id: str,
    answers: List[str],
    question_text: Optional[str] = None,
    model_name: Optional[str] = None,
    risk_level: Optional[str] = None,
    needs_more_context: bool = False,
    high_stakes: bool = False,
    rule_reason_codes: Optional[List[ReasonCode]] = None,
    rule_audit: Optional[Dict[str, Any]] = None,
    intent: Optional[str] = None,
    consequence: Optional[str] = None,
) -> DecisionOutput:

    question_txt = question_text or ""
    high_stakes = high_stakes or is_high_stakes(question_txt)

    eval_res = evaluate_answers(
        question_id=question_id,
        answers=answers,
        question_text=question_text,
        model_name=model_name,
        risk_level=risk_level,
    )

    codes = rule_reason_codes or []
    eval_flags = list(eval_res.flags)

    dbg(f"[decision] qid={question_id}")
    dbg(f"[decision] incoming_codes={codes_to_str(codes)}")
    dbg(f"[decision] eval_flags={eval_flags}")
    dbg(f"[decision] high_stakes={high_stakes}")

    decision, severity = decide_from_reason_codes(
        codes,
        high_stakes=high_stakes,
    )

    dbg(f"[decision] final={decision.value}/{severity.value}")

    return _make_ctx(
        decision=decision,
        severity=severity,
        codes=codes,
        source="policy",
        audit={
            "eval_flags": eval_flags,
            "rule_audit": rule_audit or {},
            "high_stakes": high_stakes,
        },
    )


if __name__ == "__main__":
    print("RUNNING SMOKE TEST")

    result = make_decision(
        question_id="test",
        answers=["dummy answer"],
        question_text="My INR is 1.2. How much warfarin should I take tonight?",
        model_name="test_model",
        rule_audit=None
    )

    print("RESULT:", result)