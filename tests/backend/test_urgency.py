import unittest

import _bootstrap  # noqa: F401
from app.detection.urgency_detector import detect_false_urgency
from app.nlp.preprocessing import segment_text

POSITIVES = [
    "Only 2 left!", "Only 3 items remaining.", "Hurry! Sale ends soon!",
    "Limited time offer.", "Offer ends in 08:32.", "Last chance!", "Selling fast!",
    "Almost sold out!", "Don't miss out!", "Limited stock available",
    "Hurry, offer ends soon!", "Act now!", "Buy now before it's too late!",
    "Few items left", "Only 1 remaining", "ONLY 2 LEFT!!!", "🔥 ONLY 2 LEFT!",
    "Only 5 minutes remaining!", "Sale ends in 2 hours", "Get it before the offer expires.",
    # phrases named in the official plan
    "Only 2 rooms left! Hurry!", "Limited stock", "Expires soon", "Last chance", "Act now",
]

NEGATIVES = [
    "Product is available.", "Free delivery available.", "Buy our headphones.",
    "This product has good reviews.", "Delivery takes 2 days.", "This product is available.",
    "Buy our product.", "We offer fast delivery.", "BUY NOW", "Premium Wireless Headphones",
    "TOTAL ₹967", "84% OFF", "Store opens 09:00", "Add ₹50 donation",
]


def run(text):
    return detect_false_urgency(segment_text(text))


class TestFalseUrgency(unittest.TestCase):
    def test_positives_detected(self):
        for text in POSITIVES:
            with self.subTest(text=text):
                self.assertGreaterEqual(len(run(text)), 1)

    def test_negatives_not_detected(self):
        for text in NEGATIVES:
            with self.subTest(text=text):
                self.assertEqual(run(text), [])

    def test_pattern_label(self):
        self.assertEqual(run("Only 2 left!")[0].pattern, "FALSE_URGENCY")

    def test_evidence_preserves_original_text(self):
        self.assertEqual(run("🔥 ONLY   2 LEFT!!!")[0].evidence_text, "🔥 ONLY   2 LEFT!!!")

    def test_categories(self):
        cases = {
            "Only 2 left": "Scarcity",
            "Hurry! Offer ends soon": "Time pressure",
            "Offer ends in 08:32": "Countdown",
            "Last chance to buy!": "Last chance",
        }
        for text, category in cases.items():
            with self.subTest(text=text):
                self.assertIn(category, [c for m in run(text) for c in m.categories])

    def test_rule_confidence_levels(self):
        self.assertEqual(run("Only 2 left!")[0].rule_confidence, 0.95)
        self.assertEqual(run("Limited time offer.")[0].rule_confidence, 0.80)
        self.assertEqual(run("Hurry!")[0].rule_confidence, 0.65)

    def test_confidence_always_in_range(self):
        for text in POSITIVES:
            for m in run(text):
                self.assertTrue(0.0 <= m.rule_confidence <= 1.0)


if __name__ == "__main__":
    unittest.main()
