"""Puts <repo>/backend on sys.path and disables the DeBERTa model so unit tests are deterministic."""
import os
import sys

BACKEND = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)
os.environ["DPG_DISABLE_MODEL"] = "1"
