"""Fine-tune DeBERTa-v3-base on the labeled dataset.  Run on Colab / a GPU machine.

    pip install torch transformers sentencepiece
    python ml/nlp/make_dataset.py
    python ml/nlp/train.py --epochs 5
    python ml/nlp/evaluate.py --model ml/models/nlp/deberta

Saves the epoch with the best validation macro-F1 to ml/models/nlp/deberta/.
"""
import argparse
import csv
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
LABELS = ["FALSE_URGENCY", "CONFIRM_SHAMING", "NONE"]


def read(split):
    with open(os.path.join(HERE, "data", f"{split}.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [r["text"] for r in rows], [LABELS.index(r["label"]) for r in rows]


def macro_f1(y_true, y_pred):
    scores = []
    for k in range(len(LABELS)):
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == k and p == k)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != k and p == k)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == k and p != k)
        scores.append(2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0)
    return sum(scores) / len(scores)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-name", default="microsoft/deberta-v3-base")
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--max-len", type=int, default=64)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(ROOT, "ml", "models", "nlp", "deberta"))
    args = ap.parse_args()

    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("device:", device)

    tok = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name, num_labels=len(LABELS),
        id2label=dict(enumerate(LABELS)), label2id={l: i for i, l in enumerate(LABELS)})
    # Newer transformers versions can load this checkpoint in float16. Training in fp16 gives NaN,
    # so force float32 explicitly.
    model = model.float().to(device)
    print('model dtype:', next(model.parameters()).dtype)

    train_x, train_y = read("train")
    val_x, val_y = read("val")

    def encode(texts):
        return tok(texts, truncation=True, max_length=args.max_len, padding=True, return_tensors="pt")

    steps = args.epochs * ((len(train_x) + args.batch_size - 1) // args.batch_size)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    sched = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)

    best = -1.0
    for epoch in range(1, args.epochs + 1):
        model.train()
        order = list(range(len(train_x)))
        random.shuffle(order)
        total = 0.0
        for i in range(0, len(order), args.batch_size):
            idx = order[i:i + args.batch_size]
            batch = encode([train_x[j] for j in idx]).to(device)
            labels = torch.tensor([train_y[j] for j in idx], device=device)
            loss = model(**batch, labels=labels).loss
            if not torch.isfinite(loss):
                raise RuntimeError(f'Loss is {loss.item()} at epoch {epoch}. Training stopped (see README: NaN loss).')
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sched.step(); opt.zero_grad()
            total += loss.item() * len(idx)

        model.eval()
        preds = []
        with torch.no_grad():
            for i in range(0, len(val_x), 32):
                batch = encode(val_x[i:i + 32]).to(device)
                preds += model(**batch).logits.argmax(-1).cpu().tolist()
        f1 = macro_f1(val_y, preds)
        acc = sum(1 for t, p in zip(val_y, preds) if t == p) / len(val_y)
        print(f"epoch {epoch}/{args.epochs}  train loss {total / len(train_x):.4f}  val acc {acc:.3f}  val macro-F1 {f1:.3f}")
        if f1 > best:
            best = f1
            os.makedirs(args.out, exist_ok=True)
            model.save_pretrained(args.out)
            tok.save_pretrained(args.out)
            with open(os.path.join(args.out, "labels.json"), "w", encoding="utf-8") as f:
                json.dump(LABELS, f)
            print(f"  saved best model -> {args.out}")
    print(f"done. best val macro-F1 = {best:.3f}")


if __name__ == "__main__":
    main()
