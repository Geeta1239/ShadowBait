# Member 1 — Step 2 Inspection Evidence

This folder contains the automated inspection output for the ShadowBait demo website.

## Scan command

From the repository root:

```bash
python3 scripts/member1_inspection.py
```

The runner uses a fresh Chromium context, a 1440×1000 viewport, and the local server at `http://127.0.0.1:4173` by default. Override the target with:

```bash
SHADOWBAIT_URL=http://localhost:3000 python3 scripts/member1_inspection.py
```

## Result

- **7 verified findings**
- **9 routes/pages inspected**
- **6/6 validation checks passed**
- Light-mode evidence captured
- Dark-mode evidence visibility checked
- Checkout state reset and re-tested

## Verified findings

| ID | Pattern | Route | Primary evidence |
|---|---|---|---|
| DP01 | False Urgency | `/product` | `#scarcity-text`, `#offer-timer` |
| DP02 | Basket Sneaking | `/checkout` | `#donation` initially checked |
| DP03 | Confirm Shaming | `/checkout` | `#confirm-shaming` |
| DP05 | Subscription Trap | `/subscribe` → `/cancel` | renewal checkbox and cancellation steps |
| DP06 | Interface Interference | `/interface-interference` | preferred and muted choices |
| DP07 | Bait and Switch | `/bait-switch` | `#bait-switch-status` |
| DP08 | Drip Pricing | `/checkout` | fee breakdown and `#total-price` |

## Handoff file

`member1-step2-report.json` contains:

- Page metadata
- Routes visited
- Stable selectors
- Element states
- Evidence text
- Screenshots
- Customer harm
- Ethical fixes
- Validation checks

The JSON report is the handoff input for Member 2’s detection/classification stage.
