import os
import unittest
from unittest import mock

import _bootstrap  # noqa: F401
from app.detection.fusion import fuse
from app.detection.rule_engine import analyze_text
from app.nlp.classifier import load_classifier
from app.nlp.inference import classify_text

FU, CS, NO = "FALSE_URGENCY", "CONFIRM_SHAMING", "NONE"


def result(pattern, conf, **probs):
    """Fake model output. Remaining probability goes to NONE."""
    p = {FU: 0.0, CS: 0.0, NO: 0.0}
    p.update(probs)
    p[pattern] = conf
    if pattern != NO:
        p[NO] = p[NO] or round(1 - conf, 4)
    return {"pattern": pattern, "confidence": conf, "probabilities": p}


class FakeClassifier:
    def __init__(self, mapping):
        self.mapping = mapping

    def predict(self, texts):
        return [self.mapping.get(t, result(NO, 0.99)) for t in texts]


class BrokenClassifier:
    def predict(self, texts):
        raise RuntimeError("boom")


class TestFuse(unittest.TestCase):
    def test_no_model_falls_back_to_rules(self):
        d = fuse(FU, 0.95, None)
        self.assertEqual((d.confidence, d.source), (0.95, "rules"))
        self.assertIsNone(fuse(FU, None, None))

    def test_agreement_blends_confidences(self):
        d = fuse(FU, 0.95, result(FU, 0.97))
        self.assertEqual(d.confidence, 0.96)          # 0.4*0.95 + 0.6*0.97
        self.assertEqual(d.source, "rules+model")

    def test_mild_disagreement_lowers_confidence_but_keeps_finding(self):
        d = fuse(FU, 0.95, result(NO, 0.65, **{FU: 0.30}))
        self.assertEqual(d.confidence, 0.56)          # 0.4*0.95 + 0.6*0.30
        self.assertEqual(d.source, "rules (model disagrees)")

    def test_strong_disagreement_vetoes_the_rule_hit(self):
        self.assertIsNone(fuse(FU, 0.95, result(NO, 0.90, **{FU: 0.05})))   # 0.41 < 0.50
        self.assertIsNotNone(fuse(FU, 0.95, result(NO, 0.90, **{FU: 0.05}), report_min_conf=0.0))

    def test_thresholds_are_overridable(self):
        self.assertIsNotNone(fuse(CS, None, result(CS, 0.80)))                    # passes default 0.70
        self.assertIsNone(fuse(CS, None, result(CS, 0.80), model_only_min_conf=0.9))

    def test_model_only_needs_high_confidence(self):
        d = fuse(CS, None, result(CS, 0.96))
        self.assertEqual((d.confidence, d.source), (0.86, "model_only"))
        self.assertIsNone(fuse(CS, None, result(CS, 0.60)))
        self.assertIsNone(fuse(CS, None, result(NO, 0.99)))
        self.assertIsNotNone(fuse(CS, None, result(CS, 0.60), model_only_min_conf=0.5))

    def test_confidence_never_exceeds_cap(self):
        self.assertLessEqual(fuse(FU, 0.95, result(FU, 1.0)).confidence, 0.99)


class TestEngineWithModel(unittest.TestCase):
    def test_agreement_in_finding(self):
        clf = FakeClassifier({"Only 2 left!": result(FU, 0.97)})
        f = analyze_text("Only 2 left!", classifier=clf)[0]
        self.assertEqual(f["confidence"], 0.96)
        self.assertEqual(f["detection_source"], "rules+model")
        self.assertEqual((f["rule_confidence"], f["model_confidence"]), (0.95, 0.97))
        self.assertIn("DeBERTa", f["explanation"])
        self.assertEqual(f["severity"], "MEDIUM")

    def test_mild_disagreement_still_reported_with_lower_confidence(self):
        clf = FakeClassifier({"Only 2 left!": result(NO, 0.65, **{FU: 0.30})})
        f = analyze_text("Only 2 left!", classifier=clf)[0]
        self.assertEqual(f["confidence"], 0.56)
        self.assertIn("disagrees", f["explanation"])

    def test_strong_disagreement_removes_rule_false_positive(self):
        text = "I don't want to save this address."
        self.assertEqual(len(analyze_text(text, classifier=None)), 1)          # rules alone flag it
        clf = FakeClassifier({text: result(NO, 0.97, **{CS: 0.02})})
        self.assertEqual(analyze_text(text, classifier=clf), [])               # model overrules

    def test_model_only_finding(self):
        text = "Grab it before it's gone forever"
        clf = FakeClassifier({text: result(FU, 0.96)})
        self.assertEqual(analyze_text(text, classifier=None), [])      # rules alone miss it
        f = analyze_text(text, classifier=clf)[0]
        self.assertEqual((f["rule_id"], f["detection_source"], f["confidence"]), ("DP02", "model_only", 0.86))
        self.assertIsNone(f["rule_confidence"])
        self.assertEqual(f["evidence"]["text"], text)

    def test_uncertain_model_only_not_reported(self):
        text = "Grab it before it's gone forever"
        self.assertEqual(analyze_text(text, classifier=FakeClassifier({text: result(FU, 0.60)})), [])

    def test_model_saying_none_adds_nothing(self):
        self.assertEqual(analyze_text("Free delivery available.", classifier=FakeClassifier({})), [])

    def test_broken_model_falls_back_to_rules(self):
        f = analyze_text("Only 2 left!", classifier=BrokenClassifier())
        self.assertEqual((len(f), f[0]["detection_source"], f[0]["confidence"]), (1, "rules", 0.95))

    def test_no_classifier_matches_rule_baseline(self):
        f = analyze_text("Only 2 left!", classifier=None)[0]
        self.assertEqual((f["confidence"], f["detection_source"]), (0.95, "rules"))


class TestClassifierLoading(unittest.TestCase):
    def test_disabled_by_env(self):
        self.assertIsNone(load_classifier())

    def test_missing_folder_returns_none(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("DPG_DISABLE_MODEL", None)
            self.assertIsNone(load_classifier("/definitely/not/here", force_reload=True))


class TestClassifyTextFusion(unittest.TestCase):
    def test_with_model_result(self):
        r = classify_text("No, I don't want to save money.", model_result=result(CS, 0.98))
        self.assertEqual((r["pattern"], r["source"]), (CS, "rules+model"))

    def test_model_only_none(self):
        r = classify_text("Product details", model_result=result(NO, 0.99))
        self.assertEqual(r["pattern"], NO)


if __name__ == "__main__":
    unittest.main()
