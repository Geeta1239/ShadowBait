# ShadowBaitSentinel

**DarkPatternGuard — AI-powered Ethical UX Intelligence**

ShadowBaitSentinel is a team project that scans websites, detects dark patterns, collects evidence, calculates risk, maps compliance categories, and recommends ethical UX fixes.

## Working pipeline

```text
DarkShop demo website
  → Playwright/Chromium scanner
  → DOM + text + screenshots + interaction state
  → rules + NLP detection
  → FastAPI orchestration
  → risk + compliance + SQLite
  → React dashboard + heatmap + ethical simulator
```

## Team ownership

- **Member 1:** `backend/app/crawler/` — Playwright, DOM, screenshots, interaction state
- **Member 2:** `backend/app/detection/`, `backend/app/nlp/`, `ml/nlp/` — rules and NLP
- **Member 3:** `backend/app/api/`, `database/`, `risk/`, `compliance/`, `reports/` — backend integration
- **Member 4:** `frontend/`, `demo-site/` — product experience and controlled test website
- **Everyone:** `tests/`, `docs/`, integration

## MVP detection order

1. Basket Sneaking / pre-ticked checkbox
2. False Urgency
3. Confirm Shaming
4. Misleading Discount
5. Drip Pricing / Hidden Costs
6. Subscription Trap, if time remains

## Local services

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
DarkShop: http://localhost:3000
```

## Run the demo scanner

Install the demo-site dependencies:

```bash
cd demo-site
npm install
npm run dev -- --port 3000
```

In a second terminal at the repository root, install the Python scanner and its browser:

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Run a scan:

```bash
python scripts/member1_inspection.py
```

The scanner saves output inside the repository under `evidence/scans/<scan-id>/` and `evidence/reports/<scan-id>/response.json`.

The scanner uses Playwright's installed Chromium on Windows, macOS, and Linux. Set `SHADOWBAIT_CHROMIUM_PATH` only if you intentionally want to use a specific browser executable.

See `docs/team/` for the project contract and serial workflow before implementation.
