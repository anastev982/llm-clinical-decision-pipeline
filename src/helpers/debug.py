import os
from typing import Iterable


DEBUG = os.getenv("DEBUG_PIPELINE", "0") == "1"


def dbg(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def codes_to_str(codes: Iterable) -> list[str]:
    out = []
    for c in codes:
        out.append(c.value if hasattr(c, "value") else str(c))
    return out