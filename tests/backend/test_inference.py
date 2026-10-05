import unittest

import _bootstrap  # noqa: F401
from app.nlp.inference import classify_text


class TestInference(unittest.TestCase):
    def test_false_urgency(self):
        r = classify_text("Only 2 rooms left! Hurry!")
        self.assertEqual(r["pattern"], "FALSE_URGENCY")
        self.assertEqual(r["confidence"], 0.95)

    def test_confirm_shaming(self):
        r = classify_text("No, I don't want to save money.")
        self.assertEqual((r["pattern"], r["confidence"]), ("CONFIRM_SHAMING", 0.95))

    def test_none(self):
        for text in ("No thanks.", "Product is available.", ""):
            self.assertEqual(classify_text(text)["pattern"], "NONE")

    def test_source_is_rules_until_deberta_exists(self):
        self.assertEqual(classify_text("Only 2 left!")["source"], "rules")


if __name__ == "__main__":
    unittest.main()
