import unittest

import _bootstrap  # noqa: F401
from app.nlp.preprocessing import normalize_text, segment_text


class TestPreprocessing(unittest.TestCase):
    def test_normalizes_case_spacing_punctuation_emoji(self):
        self.assertEqual(normalize_text("🔥 ONLY   2 LEFT!!!"), "only 2 left")

    def test_keeps_clock_time_and_apostrophes(self):
        self.assertEqual(normalize_text("Offer ends in 08:32."), "offer ends in 08:32")
        self.assertEqual(normalize_text("Don\u2019t miss out!"), "don't miss out")

    def test_empty_input(self):
        self.assertEqual(normalize_text(""), "")
        self.assertEqual(normalize_text(None), "")
        self.assertEqual(segment_text(""), [])

    def test_segments_preserve_original_text(self):
        segs = segment_text("🔥 ONLY   2 LEFT!!!\nGet it now. Bye!")
        self.assertEqual(segs[0].original, "🔥 ONLY   2 LEFT!!!")
        self.assertEqual(segs[0].normalized, "only 2 left")
        self.assertEqual(len(segs), 3)

    def test_lone_emoji_line_is_skipped(self):
        self.assertEqual(segment_text("🔥\n"), [])


if __name__ == "__main__":
    unittest.main()
