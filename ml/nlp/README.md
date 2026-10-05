# ml/nlp — DeBERTa training for M2

Labels: `FALSE_URGENCY`, `CONFIRM_SHAMING`, `NONE`.

## 1. Improve the dataset (do this first)
`make_dataset.py` holds ~180 hand-written seed examples. Add real phrases from real shopping sites
(urgency banners, decline buttons, normal page text, tricky normal text) to the three lists, then:
```
python ml/nlp/make_dataset.py
```
Models trained and scored on only my seed examples will look better than they really are.

## 2. Baseline (works now, no installs)
```
python ml/nlp/evaluate.py --split test
python ml/nlp/evaluate.py --split all
```

## 3. Train DeBERTa-v3-base (Google Colab, free GPU: Runtime > Change runtime type > GPU)
```
!pip install torch transformers sentencepiece
!python ml/nlp/train.py --epochs 5
!python ml/nlp/evaluate.py --model ml/models/nlp/deberta --split test
```
Training downloads `microsoft/deberta-v3-base` from Hugging Face. It saves the best epoch
(by validation macro-F1) to `ml/models/nlp/deberta/`. Download that folder and put it in the
same place in your repo.

## 4. Report honestly
Report the TEST split numbers for rules and DeBERTa side by side. The test split is small,
so say "evaluated on our own labeled set", not "state of the art".
