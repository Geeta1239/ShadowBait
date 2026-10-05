"""Pattern detectors (Phase 1 rule baseline): text segments -> PatternMatch list.

Phase 2 will add a DeBERTa classifier next to these (see nlp/); the rule engine will
then fuse rule confidence with model confidence.
"""
from __future__ import annotations

from typing import Callable, Dict, List

from ..nlp.preprocessing import Segment
from .confirm_shaming_detector import detect_confirm_shaming
from .models import PatternMatch
from .urgency_detector import detect_false_urgency

DetectorFn = Callable[[List[Segment]], List[PatternMatch]]

# rule_id -> detector. Only rules that M2 detects are registered here.
DETECTORS: Dict[str, DetectorFn] = {
    "DP02": detect_false_urgency,
    "DP03": detect_confirm_shaming,
}

__all__ = ["DETECTORS", "DetectorFn", "detect_false_urgency", "detect_confirm_shaming"]
