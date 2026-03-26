from typing import Dict, List

from src.model_apis import normalize_models
from src.helpers.metrics import upd
from src.helpers.types import FinalResult


def calculate_summary(final_result: FinalResult, models: List[str]) -> Dict[str, Dict[str, float]]:
    pairs = normalize_models(models)
    summary: Dict[str, Dict[str, float]] = {}

    total_questions = len(final_result.per_question) or 1

    for _, key in pairs:
        overall = {"eval": 0, "pass": 0, "err": 0, "false_accept": 0, "dec_ok": 0, "dec_n": 0, "sev_ok": 0, "sev_n": 0}
        model = {"eval": 0, "pass": 0, "err": 0, "false_accept": 0, "dec_ok": 0, "dec_n": 0, "sev_ok": 0, "sev_n": 0}
        guard = {"eval": 0, "pass": 0, "err": 0}

        for q_res in final_result.per_question.values():
            mr = q_res.model_results.get(key)
            if mr is None:
                continue

            upd(overall, mr)

            if mr.source == "model":
                upd(model, mr)
            elif mr.source == "guardrail":
                guard["eval"] += 1
                if mr.passed:
                    guard["pass"] += 1
                if mr.decision == "ERROR":
                    guard["err"] += 1

        overall_den = overall["eval"] or 1
        model_den = model["eval"] or 1
        guard_den = guard["eval"] or 1

        summary[key] = {
            "coverage": overall["eval"] / total_questions,
            "system_pass_rate": overall["pass"] / overall_den,
            "system_error_rate": overall["err"] / overall_den,
            "system_decision_acc": overall["dec_ok"] / (overall["dec_n"] or 1),
            "system_severity_acc": overall["sev_ok"] / (overall["sev_n"] or 1),
            "system_false_accept_rate": overall["false_accept"] / (overall["dec_n"] or 1),
            "guardrail_rate": guard["eval"] / overall_den,
            "model_call_rate": model["eval"] / overall_den,
            "model_pass_rate": model["pass"] / model_den,
            "model_error_rate": model["err"] / model_den,
            "model_decision_acc": model["dec_ok"] / (model["dec_n"] or 1),
            "model_severity_acc": model["sev_ok"] / (model["sev_n"] or 1),
            "model_false_accept_rate": model["false_accept"] / (model["dec_n"] or 1),
            "guardrail_pass_rate": guard["pass"] / guard_den,
        }

    return summary


def print_results(results: FinalResult) -> None:
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)

    show_only_fails = False

    for q_id, q_res in results.per_question.items():
        has_guardrail = any(getattr(mr, "source", None) == "guardrail" for mr in q_res.model_results.values())
        has_fail = any(not mr.passed for mr in q_res.model_results.values())

        if show_only_fails and not (has_fail or has_guardrail):
            continue

        q = q_res.question
        print(f"\n{q_id}: {q.text[:70]}...")

        guard_mrs = [mr for mr in q_res.model_results.values() if getattr(mr, "source", None) == "guardrail"]
        if guard_mrs:
            g0 = guard_mrs[0]
            print(f"  SYSTEM        → {g0.decision:8} ({g0.severity})")

        for model_key, mr in q_res.model_results.items():
            status = "✓" if mr.passed else "✗"

            exp = ""
            if getattr(mr, "expected_decision", None) is not None or getattr(mr, "expected_severity", None) is not None:
                ok = "OK" if mr.passed else "NO"
                exp = f" | exp={mr.expected_decision}/{mr.expected_severity} ({ok})"

            print(f"  {status} {model_key:12} → {mr.decision:8} ({mr.severity}){exp}")


def print_summary(summary):
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'model':10} {'cov':>6} {'sys_pass':>8} {'false_acc':>9} | {'guard':>7} {'m_call':>7} | {'m_pass':>7} {'m_false':>8}")

    for model, s in summary.items():
        print(
            f"{model:10} {s['coverage']*100:5.1f}% {s['system_pass_rate']*100:7.1f}% {s['system_false_accept_rate']*100:8.1f}% | "
            f"{s['guardrail_rate']*100:6.1f}% {s['model_call_rate']*100:6.1f}% | "
            f"{s['model_pass_rate']*100:6.1f}% {s['model_false_accept_rate']*100:7.1f}%"
        )