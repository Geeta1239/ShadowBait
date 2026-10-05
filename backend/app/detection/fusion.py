"""Rule confidence + DeBERTa confidence -> one final confidence (Phase 3).

For ONE pattern on ONE sentence:

  rules hit + model agrees      conf = 0.4*rule + 0.6*model
  rules hit + model disagrees   conf = 0.4*rule + 0.6*(model's probability for that pattern);
                                if conf < REPORT_MIN_CONFIDENCE the finding is dropped (model veto)
  rules miss + model flags it   only if model conf >= MODEL_ONLY_MIN_CONFIDENCE, conf = 0.9 * model
  no model available            conf = rule confidence                             (fallback)

All numbers are constants below. The two thresholds should be tuned on the VALIDATION split:
    python ml/nlp/evaluate.py --model ml/models/nlp/deberta --tune
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

RULE_WEIGHT = 0.4
MODEL_WEIGHT = 0.6
MODEL_ONLY_MIN_CONFIDENCE = 0.70   # starting value - tune with evaluate.py --tune
REPORT_MIN_CONFIDENCE = 0.50       # starting value - below this a rule hit is dropped when the model disagrees
MODEL_ONLY_DISCOUNT = 0.90
MAX_CONFIDENCE = 0.99

SOURCE_RULES = "rules"
SOURCE_AGREE = "rules+model"
SOURCE_DISAGREE = "rules (model disagrees)"
SOURCE_MODEL_ONLY = "model_only"


@dataclass(frozen=True)
class FusedDecision:
    confidence: float
    source: str
    rule_confidence: Optional[float]
    model_confidence: Optional[float]   # model's probability for THIS pattern


def fuse(pattern: str, rule_conf: Optional[float], model: Optional[Dict],
         model_only_min_conf: Optional[float] = None,
         report_min_conf: Optional[float] = None) -> Optional[FusedDecision]:
    """Decide whether `pattern` is reported and with what confidence. None = not reported."""
    model_only_min = MODEL_ONLY_MIN_CONFIDENCE if model_only_min_conf is None else model_only_min_conf
    report_min = REPORT_MIN_CONFIDENCE if report_min_conf is None else report_min_conf
    if model is None:
        if rule_conf is None:
            return None
        return FusedDecision(round(rule_conf, 2), SOURCE_RULES, rule_conf, None)

    top, top_conf = model["pattern"], float(model["confidence"])
    probs = model.get("probabilities", {})
    model_p = top_conf if top == pattern else float(probs.get(pattern, 0.0))

    if rule_conf is not None:
        conf = RULE_WEIGHT * rule_conf + MODEL_WEIGHT * model_p
        if conf < report_min:
            return None                      # the model overrules the rule
        source = SOURCE_AGREE if top == pattern else SOURCE_DISAGREE
        return FusedDecision(round(min(conf, MAX_CONFIDENCE), 2), source, rule_conf, round(model_p, 4))

    if top == pattern and top_conf >= model_only_min:
        conf = top_conf * MODEL_ONLY_DISCOUNT
        return FusedDecision(round(min(conf, MAX_CONFIDENCE), 2), SOURCE_MODEL_ONLY, None, round(top_conf, 4))
    return None
