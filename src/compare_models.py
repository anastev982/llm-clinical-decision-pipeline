import traceback
from typing import Any, Callable, List, Optional

from src.data_loader import load_questions, Question
from src.model_apis import normalize_models, get_answer_fn
from src.pipeline import is_high_stakes
from src.utils.env import load_env
from src.helpers.types import (
    ModelResult,
    SingleQuestionResult,
    FinalResult,
    Decision,
    Severity,
)
from src.cross_model import enrich_single_question_result
from src.helpers.normalize_models import as_decision, as_severity
from src.guardrails.runner import apply_guardrails
from src.guardrails.rules import RULES
from src.guardrails.risk_map import map_risk_to_codes
from src.guardrails.router import guardrail_route
from src.evaluators.gptmini_risk import detect_risk_gptmini
from src.decision_matrix import matrix_decide
from src.helpers.decision_runner import DecisionContext, decide_one
from src.reporting import calculate_summary, print_results, print_summary

load_env()

DEBUG = False


def dbg(*args: Any) -> None:
    if DEBUG:
        print(*args)


def build_mr(
    q: Question,
    answer: Optional[str],
    decision: Decision,
    severity: Severity,
    source: str,
    error: Optional[str] = None,
) -> ModelResult:
    mr = ModelResult(
        answer=answer,
        decision=decision,
        severity=severity,
        passed=False,
        error=error,
        source=source,
    )

    exp_dec = getattr(q, "expected_decision", None)
    exp_sev = getattr(q, "expected_severity", None)

    mr.expected_decision = exp_dec
    mr.expected_severity = exp_sev

    dec_ok = (exp_dec is None) or (mr.decision == exp_dec)
    sev_ok = (exp_sev is None) or (mr.severity == exp_sev)

    mr.decision_ok = None if exp_dec is None else dec_ok
    mr.severity_ok = None if exp_sev is None else sev_ok
    mr.false_accept = exp_dec is not None and exp_dec != "ACCEPT" and mr.decision == "ACCEPT"
    mr.passed = (exp_dec is not None or exp_sev is not None) and dec_ok and sev_ok

    return mr


def enrich_codes_with_gptmini(q: Question, codes, high_stakes: bool, audit: dict):
    # No need for call ing GPTmini if the question is not high stakes and we already have some codes.
    # If otherwise, proceed with the GPTmini call.
    if not high_stakes and codes:
        return codes, None, None, audit

    risk = detect_risk_gptmini(
        q_id=q.id,
        question_text=q.text,
        codes_list=[c.value for c in codes],
        high_stakes=high_stakes,
    ) or {}

    audit["gptmini_risk"] = risk

    intent = risk.get("intent", "informational")
    consequence = risk.get("consequence", "low")
    llm_decision, llm_severity = matrix_decide(intent, consequence)

    new_codes = map_risk_to_codes(risk.get("risk_flags", []))
    merged = list(codes)

    for code in new_codes:
        if code not in merged:
            merged.append(code)

    dbg("[risk]", risk)
    dbg("[codes]", [c.value for c in merged])

    return merged, llm_decision, llm_severity, audit


def make_ctx(q: Question, codes, audit, llm_decision, llm_severity) -> DecisionContext:
    return DecisionContext(
        question_id=q.id,
        question_text=q.text,
        rule_reason_codes=codes,
        rule_audit=audit,
        high_stakes=is_high_stakes(q.text),
        llm_decision=llm_decision,
        llm_severity=llm_severity,
    )


def apply_guardrail_result(q: Question, q_res: SingleQuestionResult, model_keys: List[str], routed):
    decision, severity, msg = routed
    # All models independently receive same guardrails result because 
    # guardrails decision does not depends of the model, it is applien before the model even 
    # answers. This is expected behavior, not a bug. 
    for key in model_keys:
        q_res.model_results[key] = build_mr(
            q=q,
            answer=msg,
            decision=decision,
            severity=severity,
            source="guardrail",
        )

def run_one_model(q: Question, ctx: DecisionContext, model_name: str, get_answer: Callable) -> ModelResult:
    try:
        answer = get_answer(model_name, q.text)
        out = decide_one(ctx, model_name=model_name, answer=answer)

        return build_mr(
            q=q,
            answer=answer,
            decision=as_decision(out.decision),
            severity=as_severity(out.severity),
            source="model",
        )
    except Exception as e:
        dbg(f"[CRASH] model={model_name} q_id={q.id}")
        dbg(traceback.format_exc())
        return build_mr(
            q=q,
            answer=None,
            decision=Decision.ERROR,
            severity=Severity.HIGH,
            source="model",
            error=str(e),
        )


def finalize_question(final_result: FinalResult, q: Question, q_res: SingleQuestionResult, ctx: DecisionContext, codes):
    enrich_single_question_result(q_res, high_stakes=ctx.high_stakes, reason_codes=codes)
    final_result.per_question[q.id] = q_res


def run_models(models: List[str], questions: List[Question], get_answer: Callable[[str, str], str]) -> FinalResult:
    pairs = normalize_models(models)
    # `keys` list extract here ones here from the normalized pairs,
    # so we dont't have to extract it every time in the loop.
    keys = [key for _, key in pairs]
    final_result = FinalResult()

    for q in questions:
        print(f"\nProcessing: {q.text[:60]}...")
        q_res = SingleQuestionResult(question=q)

        hits, codes, audit = apply_guardrails(q.text, RULES, debug=False)
        audit.setdefault("gptmini_risk", None)

        high_stakes = is_high_stakes(q.text)
        codes, llm_decision, llm_severity, audit = enrich_codes_with_gptmini(q, codes, high_stakes, audit)
        ctx = make_ctx(q, codes, audit, llm_decision, llm_severity)

        routed = guardrail_route(codes)
        if routed is not None:
            apply_guardrail_result(q, q_res, keys, routed)
            finalize_question(final_result, q, q_res, ctx, codes)
            continue

        for model_name, key in pairs:
            # 'key' is used here for storing the result of the model in q_res.model_results
            # under the appropriate key (e.g., "ChatGPT", "GPT-4").
            q_res.model_results[key] = run_one_model(q, ctx, model_name, get_answer)

        finalize_question(final_result, q, q_res, ctx, codes)

    return final_result


if __name__ == "__main__":
   # Added an API key check right after load_env(), before execution starts, 
   # so failures appear immediately with a clear message instead of crashing later during runtime.
    import os
    required_env_vars = ["OPENAI_API_KEY"]
    if missing := [var for var in required_env_vars if not os.getenv(var)]:
        raise EnvironmentError(
           f"The following environment variables are missing: {', '.join(missing)}. "
           "Check the .env file or your system environment variables."
        )

    questions = load_questions("data/clinical_questions.json")
    print(f"Loaded {len(questions)} questions")

    models = ["ChatGPT", "GPT-4"]
    print(f"\nEvaluating {len(models)} models on {len(questions)} questions...")

    results = run_models(models, questions, get_answer_fn)
    print_results(results)

    summary = calculate_summary(results, models)
    print_summary(summary)