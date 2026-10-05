"""Thin wrapper: the classifier lives in backend/app/nlp/classifier.py (single copy)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))
from app.nlp.classifier import DebertaClassifier  # noqa: E402,F401
