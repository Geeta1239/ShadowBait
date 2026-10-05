"""Central, config-driven rule engine - the entry point other members import.

    from app.detection.rule_engine import analyze_text
    findings = analyze_text(page_text, page="checkout")     # list of contract-shaped dicts

Flow:  text -> sentences -> rule detectors  (+ DeBERTa if a trained model is available)
       -> confidence fusion -> config (name / severity / recommendation) -> Finding -> de-duplicate
Without a model (or if it fails to load / run) the engine uses the rule baseline only.
"""
from __future__ import annotations

import logging
from typing import Dict, Iterable, List, Optional, Tuple, Union

from ..nlp.classifier import load_classifier
from ..nlp.preprocessing import normalize_text, segment_text
from .evidence_engine import build_evidence
from .fusion import SOURCE_AGREE, SOURCE_DISAGREE, SOURCE_MODEL_ONLY, fuse
from .models import DEFAULT_STATUS, Finding, PatternMatch
from .pattern_detector import DETECTORS
from .rules_config import RULES_CONFIG, get_rule

log = logging.getLogger(__name__)

# Every registered detector must have a rule in the config.
_unknown = set(DETECTORS) - set(RULES_CONFIG)
if _unknown:
    raise RuntimeError(f"Detectors registered for rules missing from config: {sorted(_unknown)}")

PATTERN_TO_RULE: Dict[str, str] = {get_rule(r).pattern: r for r in DETECTORS}
_RULE_ORDER = {r: i for i, r in enumerate(DETECTORS)}
_AUTO = object()   # "load the default classifier"; pass classifier=None to force rules only


def _explanation(base: str, source: str, pattern: str, model: Optional[dict], model_conf: Optional[float]) -> str:
    if source == SOURCE_AGREE:
        return f"{base} Confirmed by the DeBERTa classifier ({model_conf:.2f})."
    if source == SOURCE_DISAGREE:
        predicted = model["pattern"] if model else "?"
        return f"{base} The DeBERTa classifier disagrees (predicts {predicted}); confidence lowered."
    if source == SOURCE_MODEL_ONLY:
        return (f"The DeBERTa classifier flagged this text as {pattern.replace('_', ' ').lower()} "
                f"({model_conf:.2f}); no rule pattern matched.")
    return base


def analyze_findings(text: Union[str, Iterable[str], None], page: Optional[str] = None,
                     classifier=_AUTO) -> List[Finding]:
    """Run rules (+ optional DeBERTa) and return Finding objects."""
    if text is None:
        return []
    if not isinstance(text, str):          # tolerate a list of text snippets
        text = "\n".join(str(t) for t in text)

    segments = segment_text(text)
    if not segments:
        return []

    # 1. rule detectors: original sentence -> {pattern: PatternMatch}
    rule_hits: Dict[str, Dict[str, PatternMatch]] = {}
    for detector in DETECTORS.values():
        for match in detector(segments):
            rule_hits.setdefault(match.evidence_text, {})[match.pattern] = match

    # 2. optional model predictions (one per sentence); any failure -> rules only
    clf = load_classifier() if classifier is _AUTO else classifier
    model_results: Optional[List[dict]] = None
    if clf is not None:
        try:
            model_results = clf.predict([s.original for s in segments])
        except Exception as exc:
            log.warning("NLP model failed during prediction (%s); using rules only.", exc)

    # 3. fuse per sentence and pattern
    collected: List[Tuple[int, int, Finding]] = []
    seen = set()
    for idx, seg in enumerate(segments):
        hits = rule_hits.get(seg.original, {})
        model = model_results[idx] if model_results else None
        candidates = list(hits)
        if model and model["pattern"] in PATTERN_TO_RULE and model["pattern"] not in hits:
            candidates.append(model["pattern"])
        for pattern in candidates:
            hit = hits.get(pattern)
            decision = fuse(pattern, hit.rule_confidence if hit else None, model)
            if decision is None:
                continue
            rule_id = PATTERN_TO_RULE[pattern]
            key = (rule_id, normalize_text(seg.original))
            if key in seen:                 # same text repeated on a page -> one finding
                continue
            seen.add(key)
            cfg = get_rule(rule_id)
            base = hit.explanation if hit else ""
            collected.append((_RULE_ORDER[rule_id], idx, Finding(
                rule_id=cfg.rule_id,
                name=cfg.name,
                severity=cfg.severity,                    # fixed per rule, from config
                confidence=decision.confidence,
                status=DEFAULT_STATUS,
                evidence=build_evidence(seg.original, page=page),
                recommendation=cfg.recommendation,
                explanation=_explanation(base, decision.source, pattern, model, decision.model_confidence),
                pattern=cfg.pattern,
                rule_confidence=decision.rule_confidence,
                model_confidence=decision.model_confidence,
                detection_source=decision.source,
            )))
    collected.sort(key=lambda item: (item[0], item[1]))
    return [f for _, _, f in collected]


def analyze_text(text: Union[str, Iterable[str], None], page: Optional[str] = None,
                 classifier=_AUTO) -> List[dict]:
    """Primary integration point: page text in, list of finding dicts out."""
    return [f.to_dict() for f in analyze_findings(text, page=page, classifier=classifier)]


def get_rules_config() -> List[dict]:
    """All five rules (DP01-DP05) as plain dicts, e.g. for the API or the dashboard."""
    return [
        {"rule_id": r.rule_id, "name": r.name, "method": r.method, "severity": r.severity,
         "pattern": r.pattern, "description": r.description, "recommendation": r.recommendation,
         "detector_owner": r.detector_owner, "m2_detects": r.m2_detects}
        for r in RULES_CONFIG.values()
    ]
