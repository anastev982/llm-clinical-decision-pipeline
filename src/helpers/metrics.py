# Helper func
# Update counters for one "bucket" (overall / model / guardrail) 
from src.helpers.types import ModelResult

def upd(bucket: dict, mr: ModelResult) -> None:
        bucket["eval"] += 1
        if mr.passed:
            bucket["pass"] += 1
        if mr.decision == "ERROR":
            bucket["err"] += 1

        # false_accept should count only when we actually have expected_decision (decision_ok not None)
        if mr.false_accept:
            bucket["false_accept"] += 1

        if mr.decision_ok is not None:
            bucket["dec_n"] += 1
            if mr.decision_ok:
                bucket["dec_ok"] += 1

        if mr.severity_ok is not None:
            bucket["sev_n"] += 1
            if mr.severity_ok:
                bucket["sev_ok"] += 1
