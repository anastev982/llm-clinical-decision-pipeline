from src.pipeline import make_decision
from src.helpers.types import DecisionOutput
from src.helpers.decision_ctx import DecisionContext


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