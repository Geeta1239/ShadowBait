"""Data models: PatternMatch (detector output) and Finding (shared-contract output)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

STATUS_CANDIDATE = "CANDIDATE"   # text evidence only; no selector/screenshot yet
STATUS_VERIFIED = "VERIFIED"     # text + selector + screenshot all present
DEFAULT_STATUS = STATUS_CANDIDATE


@dataclass
class PatternMatch:
    """Raw output of a pattern detector: 'text -> pattern + confidence'."""

    pattern: str                 # e.g. "FALSE_URGENCY"
    evidence_text: str           # original sentence, exactly as on the page
    rule_confidence: float       # rule-based confidence, 0.0 - 1.0
    strength: str                # "strong" | "moderate" | "weak"
    indicator_count: int
    explanation: str
    categories: List[str] = field(default_factory=list)


@dataclass
class Finding:
    """One finding in the shared JSON-contract shape (M2's part of it)."""

    rule_id: str                 # "DP02"
    name: str                    # "False Urgency"
    severity: str                # "HIGH" | "MEDIUM" | "LOW"  (fixed per rule in config)
    confidence: float
    status: str
    evidence: Dict[str, Optional[str]]   # {text, selector, page, screenshot}
    recommendation: str
    explanation: str
    pattern: str                 # model-level label, e.g. "CONFIRM_SHAMING"
    rule_confidence: Optional[float] = None    # confidence from the rule baseline (None if rules missed)
    model_confidence: Optional[float] = None   # DeBERTa probability for this pattern (None if no model)
    detection_source: str = "rules"            # rules | rules+model | rules (model disagrees) | model_only

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "severity": self.severity,
            "confidence": self.confidence,
            "status": self.status,
            "evidence": dict(self.evidence),
            "recommendation": self.recommendation,
            "explanation": self.explanation,
            "pattern": self.pattern,
            "rule_confidence": self.rule_confidence,
            "model_confidence": self.model_confidence,
            "detection_source": self.detection_source,
        }
