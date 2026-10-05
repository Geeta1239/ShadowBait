"""Rule DP-02: False Urgency (scarcity, time pressure, countdown, last chance).

Each pattern is (category, strength, label, regex) and is matched against the
NORMALISED sentence (lowercase, no punctuation). Evidence is the ORIGINAL sentence.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from ..nlp.preprocessing import Segment
from .confidence import calculate_confidence, strongest
from .models import PatternMatch
from .rules_config import PATTERN_FALSE_URGENCY

SCARCITY = "Scarcity"
TIME_PRESSURE = "Time pressure"
COUNTDOWN = "Countdown"
LAST_CHANCE = "Last chance"


@dataclass(frozen=True)
class UrgencyPattern:
    category: str
    strength: str   # "strong" | "moderate" | "weak"
    label: str      # shown in the "reason" text
    regex: re.Pattern


def _p(category: str, strength: str, label: str, pattern: str) -> UrgencyPattern:
    return UrgencyPattern(category, strength, label, re.compile(pattern))


_CLOCK = r"\d{1,2}:\d{2}(?::\d{2})?"
_UNITS = r"(?:seconds?|secs?|minutes?|mins?|hours?|hrs?)"
_NUM = r"(?:\d+|one|two|three|four|five|a few|few)"

URGENCY_PATTERNS: List[UrgencyPattern] = [
    # --- Scarcity -----------------------------------------------------------
    _p(SCARCITY, "strong", "limited-quantity claim", rf"\bonly {_NUM}(?: \w+){{0,2}} (?:left|remaining|in stock)\b"),
    _p(SCARCITY, "strong", "few-left claim", r"\b(?:few|last few) (?:\w+ )?(?:left|remaining)\b"),
    _p(SCARCITY, "strong", "almost sold out", r"\balmost (?:sold out|gone)\b"),
    _p(SCARCITY, "moderate", "limited stock", r"\blimited (?:stock|quantity|quantities|supply|units|availability)\b"),
    _p(SCARCITY, "moderate", "selling fast", r"\b(?:selling|going) (?:out )?fast\b"),
    _p(SCARCITY, "moderate", "stock running low", r"\b(?:stock|supplies|inventory) (?:is |are )?running (?:low|out)\b"),
    _p(SCARCITY, "moderate", "will sell out", r"\b(?:will sell out|sell(?:ing)? out soon)\b"),
    _p(SCARCITY, "weak", "demand pressure", r"\b(?:in high demand|\d+ (?:people|others|customers|shoppers) (?:are )?(?:viewing|looking at|watching))\b"),
    # --- Time pressure ------------------------------------------------------
    _p(TIME_PRESSURE, "weak", "'hurry'", r"\bhurry\b"),
    _p(TIME_PRESSURE, "moderate", "'act now'", r"\bact (?:now|fast|quickly|today)\b"),
    _p(TIME_PRESSURE, "moderate", "'before it's too late'", r"\bbefore it'?s too late\b"),
    _p(TIME_PRESSURE, "moderate", "'ends soon'", r"\b(?:ends?|ending|expires?|expiring|closing|closes) (?:very )?soon\b"),
    _p(TIME_PRESSURE, "moderate", "deadline today", r"\b(?:offer|sale|deal|discount)s? (?:ends?|expires?|ending|expiring) (?:today|tonight|midnight|tomorrow)\b"),
    _p(TIME_PRESSURE, "moderate", "limited time", r"\blimited time\b"),
    _p(TIME_PRESSURE, "moderate", "'today only'", r"\b(?:today|tonight) only\b"),
    _p(TIME_PRESSURE, "moderate", "'before the offer expires'", r"\bbefore (?:the |this |our )?(?:offer|sale|deal|discount)s? (?:ends?|expires?|is over)\b"),
    _p(TIME_PRESSURE, "moderate", "'buy now before...'", r"\b(?:buy|order|book|grab|shop) now before\b"),
    _p(TIME_PRESSURE, "moderate", "'while stocks last'", r"\bwhile (?:stocks?|supplies) last\b"),
    # --- Countdown / remaining time -----------------------------------------
    _p(COUNTDOWN, "strong", "deadline with clock time",
       rf"\b(?:offer|sale|deal|discount|ends?|expires?|ending|expiring|time left|time remaining|remaining|left)\b(?: \w+){{0,3}} {_CLOCK}\b"),
    _p(COUNTDOWN, "strong", "time remaining", rf"\b\d+ ?{_UNITS} (?:left|remaining)\b"),
    _p(COUNTDOWN, "strong", "ends in N minutes/hours", rf"\b(?:ends?|expires?|ending|expiring) in (?:only |just )?\d+ ?{_UNITS}\b"),
    _p(COUNTDOWN, "moderate", "ends in N days", r"\b(?:ends?|expires?|ending|expiring) in (?:only |just )?\d+ days?\b"),
    # --- Last chance --------------------------------------------------------
    _p(LAST_CHANCE, "moderate", "'last chance'", r"\blast chance\b"),
    _p(LAST_CHANCE, "moderate", "final call", r"\bfinal (?:hours?|days?|call|chance|minutes?)\b"),
    _p(LAST_CHANCE, "moderate", "last hours/days", r"\blast (?:few )?(?:hours?|days?|minutes?)\b"),
    _p(LAST_CHANCE, "moderate", "'now or never'", r"\bnow or never\b"),
    _p(LAST_CHANCE, "weak", "'don't miss out'", r"\bdon'?t miss (?:out|this)\b"),
]


def detect_false_urgency(segments: List[Segment]) -> List[PatternMatch]:
    """Return one PatternMatch per sentence/line containing urgency language."""
    results: List[PatternMatch] = []
    for seg in segments:
        hits = [p for p in URGENCY_PATTERNS if p.regex.search(seg.normalized)]
        if not hits:
            continue
        strength = strongest(p.strength for p in hits)
        count = len(hits)
        categories = list(dict.fromkeys(p.category for p in hits))  # ordered, unique
        labels = "; ".join(p.label for p in hits)
        results.append(
            PatternMatch(
                pattern=PATTERN_FALSE_URGENCY,
                evidence_text=seg.original,
                rule_confidence=calculate_confidence(strength, count),
                strength=strength,
                indicator_count=count,
                explanation=f"Contains {', '.join(c.lower() for c in categories)} language ({labels}).",
                categories=categories,
            )
        )
    return results
