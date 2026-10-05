"""Rule DP-03: Confirm Shaming.

A sentence is scored with three kinds of signals:

    A. decline / preference wording  ("no", "skip", "I'd rather")      -> 1 point
    B. benefit / loss concepts       (savings, pay more, miss out ...) -> 1 point each (max 2)
    C. explicit self-defeating phrase ("I'd rather pay more",
       "I don't want to save")                                         -> 2 points

    score >= 4 -> strong, score == 3 -> moderate, otherwise NOT flagged.

So plain declines like "No thanks" or "No, cancel my order" (score 1) are ignored.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

from ..nlp.preprocessing import Segment
from .confidence import calculate_confidence
from .models import PatternMatch
from .rules_config import PATTERN_CONFIRM_SHAMING

MIN_SCORE_TO_FLAG = 3
STRONG_SCORE = 4
MAX_CONCEPT_POINTS = 2

# A. decline / preference wording (matched on normalised text)
DECLINE_PATTERNS = [re.compile(p) for p in (
    r"^(?:no|nope|nah)\b",
    r"\bdecline\b",
    r"\bskip\b",
    r"\bi (?:don'?t|do not) (?:want|need|care|like)\b",
    r"\bi(?: would|'d) rather\b",
    r"\bi prefer\b",
    r"\bi (?:hate|dislike)\b",
)]

# B. benefit / loss concepts
CONCEPTS: Dict[str, re.Pattern] = {name: re.compile(p) for name, p in {
    "savings": r"\bsav(?:e|es|ing|ings)\b",
    "higher cost": r"\b(?:pay(?:ing)? (?:more|extra|full price)|overpay(?:ing)?|full price|expensive|costly|higher price)\b",
    "missing out": r"\bmiss(?:ing)? out\b",
    "deals and offers": r"\b(?:deals?|discounts?|offers?|coupons?|cashback|rewards?|bonus(?:es)?|free shipping)\b",
    "protection": r"\b(?:protect(?:ion|ed)?|secur(?:e|ity)|safe(?:ty)?|insurance|warranty|coverage)\b",
    "personal stake": r"\bmy (?:account|health|family|data|future|privacy)\b",
}.items()}

# C. explicit self-defeating phrases
_DET = r"(?:(?:the|this|that|any|a|an|my|your) )?"
_ADJ = r"(?:(?:amazing|great|exclusive|special|best|awesome|incredible|free|better|extra) )?"
SELF_DEFEATING_PATTERNS = [re.compile(p) for p in (
    r"\b(?:rather|prefers?) (?:to )?(?:pay|paying|overpay|overpaying|miss|missing|lose|losing|waste|wasting|risk|risking|stay unprotected|stay vulnerable|full price|the expensive|expensive)\b",
    rf"\bi (?:don'?t|do not) (?:want|need|care (?:about|for)|like) (?:to )?{_DET}{_ADJ}(?:sav\w*|protect\w*|discounts?|deals?|offers?|bonus(?:es)?|rewards?|secur\w+|cashback|coupons?)\b",
    r"\bi (?:hate|dislike) (?:saving|savings|discounts?|deals?|money|protection|security)\b",
    r"\bi (?:like|love|enjoy) (?:paying|wasting|losing|missing|overpaying)\b",
)]


def _first_match(patterns: List[re.Pattern], text: str) -> Optional[str]:
    for pattern in patterns:
        m = pattern.search(text)
        if m:
            return m.group(0)
    return None


def score_segment(normalized: str) -> Dict[str, object]:
    """Compute the confirm-shaming score and the signals that produced it."""
    decline = _first_match(DECLINE_PATTERNS, normalized)
    concepts = [name for name, rx in CONCEPTS.items() if rx.search(normalized)]
    self_defeating = _first_match(SELF_DEFEATING_PATTERNS, normalized)

    score = (
        (1 if decline else 0)
        + min(len(concepts), MAX_CONCEPT_POINTS)
        + (2 if self_defeating else 0)
    )
    indicator_count = (1 if decline else 0) + len(concepts) + (1 if self_defeating else 0)
    return {
        "score": score,
        "indicator_count": indicator_count,
        "decline": decline,
        "concepts": concepts,
        "self_defeating": self_defeating,
    }


def detect_confirm_shaming(segments: List[Segment]) -> List[PatternMatch]:
    """Return one PatternMatch per sentence that shames the user for declining."""
    results: List[PatternMatch] = []
    for seg in segments:
        result = score_segment(seg.normalized)
        score = int(result["score"])
        if score < MIN_SCORE_TO_FLAG:
            continue
        strength = "strong" if score >= STRONG_SCORE else "moderate"
        count = int(result["indicator_count"])

        parts = []
        if result["self_defeating"]:
            parts.append(f"self-defeating phrasing ('{result['self_defeating']}')")
        if result["concepts"]:
            parts.append("refers to " + ", ".join(result["concepts"]))  # type: ignore[arg-type]
        if result["decline"]:
            parts.append("decline wording")

        results.append(
            PatternMatch(
                pattern=PATTERN_CONFIRM_SHAMING,
                evidence_text=seg.original,
                rule_confidence=calculate_confidence(strength, count),
                strength=strength,
                indicator_count=count,
                explanation="Decline option frames refusing as a loss or a poor choice: " + "; ".join(parts) + ".",
                categories=["Guilt-inducing decline"],
            )
        )
    return results
