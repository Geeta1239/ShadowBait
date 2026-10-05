"""Text preprocessing: normalise text for matching, keep originals for evidence."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Segment:
    """A sentence/line of page text.

    original   - exactly what was on the page (used as evidence)
    normalized - lowercase, punctuation-free copy (used for matching)
    """

    original: str
    normalized: str


_APOSTROPHES = str.maketrans({"\u2019": "'", "\u2018": "'", "\u02bc": "'", "`": "'", "\u00b4": "'"})
_PUNCTUATION = re.compile(r"[^\w\s':]")          # emoji, !, ?, ., commas, currency symbols...
_STRAY_COLON = re.compile(r"(?<!\d):|:(?!\d)")   # keep colons only inside clocks like 08:32
_EDGE_APOSTROPHE = re.compile(r"(?<!\w)'|'(?!\w)")  # drop quote marks, keep don't / it's
_SPACES = re.compile(r"\s+")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|[\r\n]+")


def normalize_text(text: str) -> str:
    """Lowercase, unify apostrophes, strip punctuation/emoji, collapse spaces.

    "🔥 ONLY   2 LEFT!!!"  ->  "only 2 left"
    """
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", text).translate(_APOSTROPHES).lower()
    t = _PUNCTUATION.sub(" ", t)
    t = _STRAY_COLON.sub(" ", t)
    t = _EDGE_APOSTROPHE.sub(" ", t)
    return _SPACES.sub(" ", t).strip()


def segment_text(text: str) -> List[Segment]:
    """Split page text into sentence/line segments, keeping original wording."""
    segments: List[Segment] = []
    for piece in _SENTENCE_SPLIT.split(text or ""):
        original = piece.strip()
        normalized = normalize_text(original)
        if normalized:  # skip pieces with no real words (e.g. a lone emoji)
            segments.append(Segment(original=original, normalized=normalized))
    return segments
