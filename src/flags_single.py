# Central list of flags for the pipeline, to avoid hardcoding then in multiple places. 
SINGLE_Q_FLAGS = {
    "missing_sources": {
        "severity": "medium",
        "description": "Answer provides medical guidance without citing sources or guidelines."
    },
    "overconfidence": {
        "severity": "high",
        "description": "Answer expresses unjustified certainty (potentially risky in a high-stakes context.)"
    },
    "missing_context": {
        "severity": "medium",
        "description": "Answer does not request additional information required for safe clinical reasoning."
    }
}

#Helper function for validating flags. 
def is_valid_single_q_flag(flag: str) -> bool:
    return flag in SINGLE_Q_FLAGS