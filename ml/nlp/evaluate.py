"""Evaluate classifiers on the labeled dataset.

    python ml/nlp/evaluate.py                       # rule baseline (Phase 1), test split
    python ml/nlp/evaluate.py --split all           # rule baseline on every example
    python ml/nlp/evaluate.py --model ml/models/nlp/deberta     # DeBERTa alone
    python ml/nlp/evaluate.py --model ml/models/nlp/deberta --fusion   # rules + DeBERTa fused
    python ml/nlp/evaluate.py --model ml/models/nlp/deberta --tune     # pick fusion thresholds on the VAL split
    python ml/nlp/evaluate.py --model ml/models/nlp/deberta --fusion --model-only-min 0.6 --report-min 0.5
    python ml/nlp/evaluate.py --compare                          # table of the saved results
"""
import argparse
import csv
import json
import os
import sys
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "backend"))

LABELS = ["FALSE_URGENCY", "CONFIRM_SHAMING", "NONE"]


def load(split: str):
    with open(os.path.join(HERE, "data", f"{split}.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [r["text"] for r in rows], [r["label"] for r in rows]


def metrics(y_true: List[str], y_pred: List[str]) -> Dict:
    per_class = {}
    for lab in LABELS:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == lab and p == lab)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != lab and p == lab)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == lab and p != lab)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        per_class[lab] = {"precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3),
                          "support": sum(1 for t in y_true if t == lab)}
    accuracy = sum(1 for t, p in zip(y_true, y_pred) if t == p) / max(len(y_true), 1)
    macro_f1 = sum(c["f1"] for c in per_class.values()) / len(LABELS)
    confusion = {t: {p: sum(1 for a, b in zip(y_true, y_pred) if a == t and b == p) for p in LABELS} for t in LABELS}
    return {"accuracy": round(accuracy, 3), "macro_f1": round(macro_f1, 3),
            "per_class": per_class, "confusion": confusion}


def predict_rules(texts: List[str]) -> List[str]:
    from app.nlp.inference import classify_text
    return [classify_text(t)["pattern"] for t in texts]


def predict_model(texts: List[str], model_dir: str) -> List[str]:
    sys.path.insert(0, HERE)
    from inference import DebertaClassifier
    clf = DebertaClassifier(model_dir)
    return [r["pattern"] for r in clf.predict(texts)]


def predict_fused(texts: List[str], model_dir: str, model_only_min=None, report_min=None) -> List[str]:
    sys.path.insert(0, HERE)
    from inference import DebertaClassifier
    from app.nlp.inference import classify_text
    results = DebertaClassifier(model_dir).predict(texts)
    return [classify_text(t, model_result=r, model_only_min_conf=model_only_min,
                          report_min_conf=report_min)["pattern"] for t, r in zip(texts, results)]


def tune(model_dir: str, split: str = "val") -> None:
    """Try fusion thresholds on the VALIDATION split (never tune on test)."""
    sys.path.insert(0, HERE)
    from inference import DebertaClassifier
    from app.nlp.inference import classify_text
    texts, y_true = load(split)
    results = DebertaClassifier(model_dir).predict(texts)

    tops = sorted(r["confidence"] for r in results)
    print(f"\nDeBERTa top-class confidence on '{split}' ({len(texts)} samples): "
          f"min {tops[0]:.2f}  median {tops[len(tops) // 2]:.2f}  max {tops[-1]:.2f}")
    flagged = sorted(r["confidence"] for r in results if r["pattern"] != "NONE")
    if flagged:
        print(f"  when it flags a pattern ({len(flagged)}): min {flagged[0]:.2f}  median {flagged[len(flagged) // 2]:.2f}  max {flagged[-1]:.2f}")
    print(f"  samples with confidence >= 0.90: {sum(1 for c in tops if c >= 0.90)} of {len(tops)}")

    rows = []
    for mo in (0.5, 0.6, 0.7, 0.8, 0.9):
        for rp in (0.0, 0.3, 0.4, 0.5, 0.6):
            preds = [classify_text(t, model_result=r, model_only_min_conf=mo, report_min_conf=rp)["pattern"]
                     for t, r in zip(texts, results)]
            m = metrics(y_true, preds)
            rows.append((m["macro_f1"], m["accuracy"], mo, rp))
    rows.sort(key=lambda r: (-r[0], -r[1], r[2], r[3]))
    alone = metrics(y_true, [r["pattern"] for r in results])
    rules = metrics(y_true, predict_rules(texts))
    print(f"\nreference on '{split}':  rules macro-F1 {rules['macro_f1']:.3f} | DeBERTa alone macro-F1 {alone['macro_f1']:.3f}")
    print("\nbest fusion settings (macro-F1, accuracy, model-only-min, report-min):")
    for f1, acc, mo, rp in rows[:8]:
        print(f"  {f1:.3f}   {acc:.3f}    {mo:.1f}    {rp:.1f}")
    f1, acc, mo, rp = rows[0]
    print(f"\nsuggested:  --model-only-min {mo} --report-min {rp}")
    print("Small validation sets make this noisy: prefer settings that are in a plateau of good scores, not a single spike.")
    print("Then run once on test:  python ml/nlp/evaluate.py --model <dir> --fusion "
          f"--model-only-min {mo} --report-min {rp} --split test")


def compare(split: str) -> None:
    print(f"\n== comparison on '{split}' split ==")
    print(f"{'system':<10}{'accuracy':>10}{'macro-F1':>10}{'samples':>9}")
    for name in ("rules", "deberta", "fused"):
        path = os.path.join(HERE, "results", f"{name}_{split}.json")
        if not os.path.exists(path):
            print(f"{name:<10}  (not run yet)")
            continue
        with open(path, encoding="utf-8") as f:
            m = json.load(f)
        print(f"{name:<10}{m['accuracy']:>10.3f}{m['macro_f1']:>10.3f}{m['samples']:>9}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test", choices=["train", "val", "test", "all"])
    ap.add_argument("--model", default=None, help="folder of a fine-tuned DeBERTa model")
    ap.add_argument("--fusion", action="store_true", help="evaluate rules + DeBERTa fused (needs --model)")
    ap.add_argument("--compare", action="store_true", help="print a table of saved results and exit")
    ap.add_argument("--tune", action="store_true", help="sweep fusion thresholds on the val split (needs --model)")
    ap.add_argument("--model-only-min", type=float, default=None, help="fusion: min DeBERTa confidence when rules miss")
    ap.add_argument("--report-min", type=float, default=None, help="fusion: drop rule hits whose fused confidence is below this")
    args = ap.parse_args()
    if args.compare:
        compare(args.split)
        return
    if (args.fusion or args.tune) and not args.model:
        ap.error("--fusion / --tune need --model")
    if args.tune:
        tune(args.model)
        return

    texts, y_true = load(args.split)
    name = "fused" if args.fusion else ("deberta" if args.model else "rules")
    if args.fusion:
        y_pred = predict_fused(texts, args.model, args.model_only_min, args.report_min)
    elif args.model:
        y_pred = predict_model(texts, args.model)
    else:
        y_pred = predict_rules(texts)
    m = metrics(y_true, y_pred)

    print(f"\n== {name} on '{args.split}' split ({len(texts)} samples) ==")
    print(f"accuracy {m['accuracy']:.3f}   macro-F1 {m['macro_f1']:.3f}\n")
    print(f"{'class':<16}{'precision':>10}{'recall':>9}{'f1':>7}{'support':>9}")
    for lab, c in m["per_class"].items():
        print(f"{lab:<16}{c['precision']:>10.3f}{c['recall']:>9.3f}{c['f1']:>7.3f}{c['support']:>9}")
    print("\nconfusion (rows = true, columns = predicted):")
    print(" " * 16 + "".join(f"{l[:10]:>12}" for l in LABELS))
    for t in LABELS:
        print(f"{t:<16}" + "".join(f"{m['confusion'][t][p]:>12}" for p in LABELS))
    errors = [(t, a, b) for t, a, b in zip(texts, y_true, y_pred) if a != b]
    print(f"\nmistakes: {len(errors)}")
    for t, a, b in errors:
        print(f"  true={a:<15} pred={b:<15} {t}")

    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    out = os.path.join(HERE, "results", f"{name}_{args.split}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({**m, "samples": len(texts), "mistakes": [list(e) for e in errors]}, f, indent=2, ensure_ascii=False)
    print(f"\nsaved -> {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
