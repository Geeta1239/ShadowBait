"""Backward-compatible single-text classification API for M2.

The newer detection pipeline lives in ``app.detection.rule_engine`` and returns
shared-contract findings.  This module provides the small legacy API used by
older integrations and tests:

    classify_text("Only 2 left!")
      -> {"pattern": "FALSE_URGENCY", "confidence": 0.95, "source": "rules"}

It deliberately uses the same preprocessing and rule detectors as the main
engine, and can optionally fuse a supplied DeBERTa-style model result.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.detection.fusion import fuse
from app.detection.pattern_detector import DETECTORS
from app.detection.rules_config import PATTERN_NONE
from app.nlp.classifier import load_classifier
from app.nlp.preprocessing import segment_text

# The detector map is keyed by rule id; its PatternMatch values carry the model
# label and deterministic rule confidence.


def _best_rule_match(text: str):
    """Return the strongest rule match for one text, or ``None``."""
    segments = segment_text(text)
    matches = []
    for detector in DETECTORS.values():
        matches.extend(detector(segments))
    if not matches:
        return None
    # Prefer confidence first, then stronger indicator coverage.  This keeps
    # the result deterministic if a sentence matches both detectors.
    return max(matches, key=lambda item: (item.rule_confidence, item.indicator_count))


def _model_prediction(text: str) -> Optional[Dict[str, Any]]:
    """Run the optional trained classifier for one text, if available."""
    classifier = load_classifier()
    if classifier is None:
        return None
    try:
        return classifier.predict([text])[0]
    except Exception:
        # The main rule engine follows the same graceful fallback policy.
        return None


def classify_text(text: str, model_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Classify one text snippet using rules and optional model fusion.

    ``model_result`` is accepted for deterministic tests and for callers that
    already ran the model.  When omitted, a configured DeBERTa classifier is
    loaded if available; otherwise the rule baseline is returned.
    """
    text = text or ""
    match = _best_rule_match(text)
    supplied_model = model_result if model_result is not None else _model_prediction(text)

    if match is None:
        if supplied_model and supplied_model.get("pattern") not in (None, PATTERN_NONE):
            pattern = str(supplied_model["pattern"])
            confidence = float(supplied_model.get("confidence", 0.0))
            return {
                "pattern": pattern,
                "confidence": round(confidence * 0.9, 2),
                "source": "model_only",
                "model_confidence": confidence,
                "probabilities": supplied_model.get("probabilities", {}),
            }
        return {
            "pattern": PATTERN_NONE,
            "confidence": float(supplied_model.get("confidence", 0.0)) if supplied_model else 0.0,
            "source": "rules" if supplied_model is None else "model",
            "probabilities": supplied_model.get("probabilities", {}) if supplied_model else {},
        }

    # The detector's pattern is the model-level label expected by the tests
    # and by the M1-M2 adapter.  fuse() applies the shared confidence policy.
    decision = fuse(match.pattern, match.rule_confidence, supplied_model)
    if decision is None:
        return {
            "pattern": PATTERN_NONE,
            "confidence": 0.0,
            "source": "rules (model disagrees)",
            "rule_confidence": match.rule_confidence,
        }

    return {
        "pattern": match.pattern,
        "confidence": decision.confidence,
        "source": decision.source,
        "rule_confidence": decision.rule_confidence,
        "model_confidence": decision.model_confidence,
        "evidence_text": match.evidence_text,
        "explanation": match.explanation,
        "probabilities": supplied_model.get("probabilities", {}) if supplied_model else {},
    }


__all__ = ["classify_text"]
