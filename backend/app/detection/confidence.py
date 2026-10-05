"""Deterministic, explainable confidence calculation.

This is a RULE-BASED score, not a trained probability.

    strength   base   ceiling
    strong     0.95   0.95     exact, unambiguous pattern
    moderate   0.80   0.90     clear pattern; +0.05 per extra indicator
    weak       0.65   0.75     suggestive wording; +0.05 per extra indicator
"""
from __future__ import annotations

from typing import Iterable

STRENGTH_ORDER = {"weak": 0, "moderate": 1, "strong": 2}
BASE_CONFIDENCE = {"strong": 0.95, "moderate": 0.80, "weak": 0.65}
MAX_CONFIDENCE = {"strong": 0.95, "moderate": 0.90, "weak": 0.75}
BONUS_PER_EXTRA_INDICATOR = 0.05


def strongest(strengths: Iterable[str]) -> str:
    """Return the strongest label among several ("strong" > "moderate" > "weak")."""
    return max(strengths, key=lambda s: STRENGTH_ORDER[s])


def calculate_confidence(strength: str, indicator_count: int = 1) -> float:
    """Confidence in [0, 1] from the strongest pattern and number of indicators."""
    if strength not in BASE_CONFIDENCE:
        raise ValueError(f"Unknown strength: {strength!r}")
    extra = max(indicator_count - 1, 0)
    score = BASE_CONFIDENCE[strength] + BONUS_PER_EXTRA_INDICATOR * extra
    return round(min(score, MAX_CONFIDENCE[strength]), 2)
