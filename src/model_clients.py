# ModelClient is a wrapper around model calls.
# We use it for:
# - Standardization of the interface: client.ask(question) -> (answer, metadata)
# - To centralize latency measurement and error handling
# - To keep evaluation logic (compare_models) clean and backend-agnostic
# - To enable future extensions (retries, caching, token usage, cost tracking, tracing)
#
# This design allows the system to go from a simple research prototype
# to a more robust experimental or production-ready evaluation framework.



from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import time

from src.model_apis import get_answer_fn

@dataclass
class ModelCallMeta:
    latency_s: float
    error: Optional[str] = None

@dataclass
class ModelClient:
    model_name: str

    def ask(self, question: str) -> tuple[Optional[str], ModelCallMeta]:
        t0 = time.time()
        try:
            answer = get_answer_fn(self.model_name, question)
            return answer, ModelCallMeta(latency_s=time.time() - t0, error=None)
        except Exception as e:
            return None, ModelCallMeta(latency_s=time.time() - t0, error=repr(e))