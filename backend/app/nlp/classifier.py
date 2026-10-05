"""DeBERTa-v3-base classifier wrapper with graceful fallback.

If torch/transformers or the trained model folder are missing, load_classifier() returns None
and the engine keeps working with the rule baseline only.

Model folder:  env DPG_NLP_MODEL_DIR, else <repo>/ml/models/nlp/deberta
Disable model: env DPG_DISABLE_MODEL=1
"""
from __future__ import annotations

import json
import logging
import os
from typing import Dict, List, Optional

log = logging.getLogger(__name__)

ENV_MODEL_DIR = "DPG_NLP_MODEL_DIR"
ENV_DISABLE = "DPG_DISABLE_MODEL"
DEFAULT_MODEL_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models", "nlp", "deberta"))


class DebertaClassifier:
    """Loads a fine-tuned model folder (from ml/nlp/train.py) and predicts pattern + confidence."""

    def __init__(self, model_dir: str, max_len: int = 64, device: Optional[str] = None):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        if not os.path.isdir(model_dir):
            raise FileNotFoundError(f"Model folder not found: {model_dir}")
        self.torch = torch
        self.max_len = max_len
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        # .float(): newer transformers versions may load this checkpoint as float16
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir).float().to(self.device).eval()
        with open(os.path.join(model_dir, "labels.json"), encoding="utf-8") as f:
            self.labels: List[str] = json.load(f)

    def predict(self, texts: List[str], batch_size: int = 32) -> List[Dict]:
        """[{'pattern': 'FALSE_URGENCY', 'confidence': 0.97, 'probabilities': {...}}, ...]"""
        results: List[Dict] = []
        for i in range(0, len(texts), batch_size):
            enc = self.tokenizer(texts[i:i + batch_size], truncation=True, max_length=self.max_len,
                                 padding=True, return_tensors="pt").to(self.device)
            with self.torch.no_grad():
                probs = self.torch.softmax(self.model(**enc).logits, dim=-1).cpu().tolist()
            for p in probs:
                best = max(range(len(p)), key=lambda k: p[k])
                results.append({"pattern": self.labels[best], "confidence": round(p[best], 4),
                                "probabilities": {l: round(v, 4) for l, v in zip(self.labels, p)}})
        return results


_CACHE: Dict[str, Optional[DebertaClassifier]] = {}


def load_classifier(model_dir: Optional[str] = None, force_reload: bool = False) -> Optional[DebertaClassifier]:
    """Return a loaded classifier, or None if disabled / not installed / model folder missing."""
    if os.environ.get(ENV_DISABLE) == "1":
        return None
    path = model_dir or os.environ.get(ENV_MODEL_DIR) or DEFAULT_MODEL_DIR
    if not force_reload and path in _CACHE:
        return _CACHE[path]
    clf: Optional[DebertaClassifier] = None
    if not os.path.isdir(path):
        log.info("NLP model folder not found (%s); using rule baseline only.", path)
    else:
        try:
            clf = DebertaClassifier(path)
            log.info("Loaded DeBERTa classifier from %s", path)
        except Exception as exc:  # missing torch/transformers, bad files, ...
            log.warning("Could not load DeBERTa model (%s); using rule baseline only.", exc)
    _CACHE[path] = clf
    return clf
