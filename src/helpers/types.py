from typing import Optional, List, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from src.data_loader import Question
from enum import Enum

if TYPE_CHECKING:
    from src.guardrails.policy_codes import ReasonCode


class Decision(str, Enum):
    ACCEPT = "ACCEPT"
    WARN = "WARN"
    ESCALATE = "ESCALATE"
    REFUSE = "REFUSE"
    DEFER = "DEFER"
    ERROR = "ERROR"
    
class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
    
@dataclass
class ModelResult:
    answer: Optional[str]
    decision: Decision          # "ACCEPT", "WARN", "DEFER", "ESCALATE", "REFUSE", "ERROR"
    severity: Severity          # "low", "medium", "high"
    passed: bool
    error: Optional[str] = None
    audit: Optional[Dict[str, Any]] = None
    source: str = "model"
    expected_decision: Optional[Decision] = None
    expected_severity: Optional[Severity] = None
    decision_ok: Optional[bool] = None
    severity_ok: Optional[bool] = None
    false_accept: Optional[bool] = None  # expected != ACCEPT but got ACCEPT


@dataclass
class CrossModelAnalysis:
    contradictions: Optional[List[str]] = None
    avg_similarity: float = 0.0
    consensus: float = 0.0  # % models with "passed"
    decision_consensus: float = 0.0 # % models that agreed on model severity

@dataclass
class SingleQuestionResult:
    question: Question
    model_results: Dict[str, ModelResult] = field(default_factory=dict)
    cross_model: CrossModelAnalysis = field(default_factory=CrossModelAnalysis)
    system_decision: Optional[Decision] = None
    system_severity: Optional[Severity] = None
    guardrail_audit: Optional[dict] = None
    safe_msg: Optional[str] = None


@dataclass
class FinalResult:
    per_question: Dict[str, SingleQuestionResult] = field(default_factory=dict)
    summary: Dict[str, Dict[str, float]] = field(default_factory=dict)

@dataclass
class DecisionOutput:
    decision: Decision
    severity: Severity
    reason_codes: List[str] = field(default_factory=list)
    audit: Dict[str, Any] = field(default_factory=dict)
    source: str = "policy"
    
@dataclass
class DecisionTrace:
    needs_more_context: bool = False
    short_reason: str = ""
    risk_flags: List[str] = field(default_factory=list)
    raw_text: str = ""
    model: str = ""
    question_id: str = ""
    category: str = ""
    iteration: int = 0
    repeat_paraphrase: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class RuleHit:
    code: 'ReasonCode'           # ReasonCode enum
    severity: str                # "low"/"medium"/"high" or None
    info: Dict[str, Any] = field(default_factory=dict)