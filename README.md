# ShadowBait

## Explainable dark-pattern inspection and ethical UX auditing prototype

ShadowBait is a controlled research prototype for inspecting shopping interfaces for dark-pattern signals. The system combines a separate consumer-facing demo site, a separate ShadowBait inspection console, browser automation, structured evidence capture, rule-based/NLP classification, risk scoring, compliance-oriented mapping, SQLite persistence, and saved results.

The current implementation is validated against the controlled **Morrow Market** demo website. Morrow Market is intentionally presented as a normal e-commerce storefront; its observable interface behavior gives ShadowBait repeatable evidence to capture. The ShadowBait platform owns the inspection console, guidelines, customer-impact explanation, interactive diff, case studies, and report.

> **Technical scope:** The current prototype is not a fully generic crawler for every arbitrary public website. It is a controlled inspection and evidence pipeline designed to expand toward generic DOM discovery, user-journey crawling, browser-extension analysis, and larger annotated datasets.

---

## 1. Design goals

The project was designed around these goals:

1. **Evidence before classification** — a pattern should be supported by visible text, DOM state, selector, page, and screenshot evidence.
2. **Modular team ownership** — website, scanner, detection, backend, storage, and dashboard layers remain separable.
3. **Explainable results** — every classification should expose confidence, severity, source, explanation, and recommendation.
4. **Reproducible validation** — controlled fixtures and a clean comparison page provide repeatable positive and negative tests.
5. **Persistent results** — a completed scan should remain available after the scan process finishes.
6. **Safe prototype boundaries** — no payments, authentication, malware, or destructive interaction is required.
7. **Incremental development** — each workflow stage can be tested before the next stage is added.

---

## 2. System architecture

```text
┌──────────────────────────────┐
│ Morrow Market storefront     │
│ React + Vite · normal UI      │
└──────────────┬───────────────┘
               │ target URL
               ▼
┌──────────────────────────────┐
│ Playwright inspection layer  │
│ Chromium, DOM, text, state,  │
│ selectors, screenshots       │
└──────────────┬───────────────┘
               │ M1 evidence
               ▼
┌──────────────────────────────┐
│ M1 → M2 shared adapter       │
│ Normalizes evidence and      │
│ preserves screenshot context │
└──────────────┬───────────────┘
               │ normalized evidence text
               ▼
┌──────────────────────────────┐
│ M2 detection layer           │
│ Rules, NLP compatibility,   │
│ confidence, severity        │
└──────────────┬───────────────┘
               │ findings
               ▼
┌──────────────────────────────┐
│ Scan orchestration API       │
│ Lifecycle, status, report    │
│ and evidence endpoints       │
└──────────────┬───────────────┘
               │ combined report
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐  ┌───────────────┐
│ Risk scoring │  │ Compliance    │
│ severity ×   │  │ mapping and   │
│ confidence   │  │ recommendations│
└──────┬───────┘  └───────┬───────┘
       └────────┬─────────┘
                ▼
┌──────────────────────────────┐
│ SQLite + JSON evidence files  │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ ShadowBait platform frontend  │
│ findings, impact, diff,       │
│ guidelines, cases, download   │
└──────────────────────────────┘
```

### Runtime services

| Service | Default address | Purpose |
|---|---|---|
| Morrow Market/Vite | `http://localhost:3000` | Separate controlled target website and fixtures |
| ShadowBait/Vite | `http://localhost:3100` | Separate inspection console and presentation UI |
| Inspection API | `http://127.0.0.1:5050` | Playwright, SSE, scan API, report generation |
| SQLite | `evidence/shadowbait.sqlite3` | Scan history and structured persistence |

Both Vite development servers proxy `/api` and `/health` to the inspection API through their respective `vite.config.js` files. ShadowBait receives the target site URL explicitly; it no longer assumes that `window.location.origin` is the scan target.

The current backend uses Python’s standard-library threaded HTTP server plus Playwright. The orchestration contract is framework-independent and can be migrated to FastAPI later without changing the evidence or report format.

---

## 3. Repository structure

```text
ShadowBait/
├── backend/
│   ├── inspection_server.py
│   └── app/
│       ├── api/
│       │   └── scan_orchestrator.py
│       ├── compliance/
│       │   └── mapping.py
│       ├── database/
│       │   └── repository.py
│       ├── detection/
│       │   ├── evidence_engine.py
│       │   ├── fusion.py
│       │   ├── models.py
│       │   ├── pattern_detector.py
│       │   ├── rule_engine.py
│       │   └── rules_config.py
│       ├── integration/
│       │   └── m1_m2_adapter.py
│       ├── nlp/
│       │   └── preprocessing and inference modules
│       └── risk/
│           └── scoring.py
├── demo-site/
│   ├── src/main.jsx
│   ├── src/styles.css
│   ├── public/
│   ├── vite.config.js
│   └── package.json
├── prototype/
│   ├── src/main.jsx
│   ├── src/styles.css
│   ├── public/manus-routes.json
│   ├── vite.config.js
│   └── package.json
├── docs/
│   ├── architecture/
│   ├── reference documentation/
│   └── team/
├── evidence/
├── scripts/
│   ├── member1_inspection.py
│   ├── verify_scan_outputs.py
│   └── clean_page_check.py
├── tests/
│   ├── backend/
│   ├── integration/
│   ├── scanner/
│   └── frontend/
├── requirements.txt
└── README.md
```

### Ownership boundaries

| Area | Responsibility | Main implementation |
|---|---|---|
| Controlled website | Pages, fixtures, stable selectors, clean comparison page | `demo-site/` |
| M1 evidence | Browser navigation, DOM, screenshots, state | `backend/inspection_server.py`, `scripts/` |
| M2 detection | Rules, text normalization, confidence, pattern classification | `backend/app/detection/`, `backend/app/nlp/` |
| Integration | Shared evidence contract and M1/M2 merge | `backend/app/integration/` |
| Backend | Scan lifecycle, API, report assembly | `backend/inspection_server.py`, `backend/app/api/` |
| Persistence | SQLite schema and report/evidence storage | `backend/app/database/` |
| Risk | Severity/confidence/completeness scoring | `backend/app/risk/` |
| Compliance | Technical category, harm, principle, recommendation mapping | `backend/app/compliance/` |
| Demo UI | Target pages, fixtures, safe comparison flows | `demo-site/src/` |
| Prototype UI | URL input, inspection stream, evidence, results, case studies, architecture | `prototype/src/` |

---

## 4. End-to-end data flow

### Step 1 — Controlled website

The Morrow Market site contains predictable interface fixtures. Each fixture has a known route, selector, expected state, visible wording, and expected interpretation.

### Step 2 — Browser inspection

Playwright opens the relevant route with Chromium and records:

- Requested and final URL
- Page title
- Route
- Visible text
- Selector
- Visibility
- Enabled/disabled state
- Checkbox state
- Bounding box
- Selected computed styles
- Full-page screenshot
- HTML capture
- Visible-text JSON

### Step 3 — M1 evidence package

The browser observation is stored as a structured finding. For stateful fixtures, the scanner also performs a safe comparison action:

- Basket Sneaking: checked donation → unchecked donation
- Subscription Trap: subscribe route → cancellation route

The original state and screenshot remain attached to the finding.

### Step 4 — M1/M2 adapter

`backend/app/integration/m1_m2_adapter.py` converts scanner fields into the shared detection shape. It passes evidence text to the M2 engine and attaches the original selector, page, screenshot, and scanner state to every returned classification.

### Step 5 — M2 detection

The current M2 engine uses configured rules and optional NLP compatibility/inference. The active language-level detectors support:

- False Urgency
- Confirm Shaming

M1/M3-owned structural and price-flow fixtures are still captured and reported even when they do not produce an M2 language finding.

### Step 6 — Risk calculation

For each captured scanner item, the system uses the strongest M2 result when available. Otherwise, it scores the verified M1 evidence using its configured/demo severity. This avoids double-counting one pattern once as M1 and again as M2.

```text
finding score = severity weight × confidence × evidence completeness
```

### Step 7 — Compliance mapping

Each finding receives a technical mapping containing:

- Pattern category
- Choice/privacy principle
- Description
- Potential harm
- Ethical recommendation
- Verification status
- Scope/source metadata

This mapping is designed for technical review and does not automatically determine a legal violation.

### Step 8 — Persistence and dashboard

The complete report is written to JSON, normalized records are stored in SQLite, and the dashboard retrieves the saved report through the scan API.

---

## 5. Controlled Morrow Market fixtures

| ID | Pattern | Route | Evidence target | Current detection role |
|---|---|---|---|---|
| `DP01` | False Urgency | `/product` | `#scarcity-text` and `#offer-timer` | M1 evidence + M2 language |
| `DP02` | Basket Sneaking | `/checkout` | `#donation` | M1/M3 structural evidence |
| `DP03` | Confirm Shaming | `/checkout` | `#confirm-shaming` | M2 language |
| `DP05` | Subscription Trap | `/subscribe` | `data-ccpa-pattern` fixture | M1/M3 flow evidence |
| `DP06` | Interface Interference | `/interface-interference` | `data-ccpa-pattern` fixture | M1/M3 visual evidence |
| `DP07` | Bait and Switch | `/bait-switch` | `#bait-switch-status` | M1/M3 flow evidence |
| `DP08` | Drip Pricing | `/checkout` | `data-ccpa-pattern` fixture | M1/M3 price-flow evidence |

The wider CCPA lab also contains simulated or excluded examples. Those entries are catalogue content and are not all part of the live seven-pattern scanner list.

---

## 6. Installation

### Prerequisites

- Python 3.11 or newer
- Node.js 18 or newer
- npm
- Git
- Chromium installed through Playwright

### Clone

```bash
git clone https://github.com/Geeta1239/ShadowBait.git
cd ShadowBait
```

### Python environment — macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### Python environment — Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

If PowerShell activation is unavailable:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m playwright install chromium
```

### Frontend dependencies

```bash
cd demo-site
npm install
cd ..
cd prototype
npm install
cd ..
```

---

## 7. Run the local system

Use three terminals from the repository root.

### Terminal 1 — Morrow Market target website

```bash
cd demo-site
npm run dev -- --port 3000
```

Useful routes:

```text
http://localhost:3000/product
http://localhost:3000/checkout
http://localhost:3000/subscribe
http://localhost:3000/clean-page
```

The demo site is the website ShadowBait inspects. Its navigation no longer contains the inspection console.

### Terminal 2 — ShadowBait prototype

```bash
cd prototype
npm run dev -- --port 3100
```

Open `http://localhost:3100`, choose **New Inspection**, and enter the demo-site URL, normally `http://127.0.0.1:3000` for a local presentation.

### Terminal 3 — inspection API

```bash
PYTHONPATH=backend python backend/inspection_server.py
```

Health check:

```bash
curl http://127.0.0.1:5050/health
```

The prototype proxies `/api` to the API and starts the live stream with the explicit target URL entered by the presenter.

Optional environment variables:

```text
INSPECTION_API_HOST       API bind address; default 0.0.0.0
INSPECTION_API_PORT       API port; default 5050
SHADOWBAIT_TARGET_URL     default scan target; default http://127.0.0.1:3000
SHADOWBAIT_EVIDENCE_DIR   evidence root; default repository/evidence
SHADOWBAIT_DB_PATH        SQLite path; default evidence/shadowbait.sqlite3
SHADOWBAIT_CHROMIUM_PATH  optional explicit Chromium executable
```

---

## 8. API contract

### Start a scan

```text
POST /api/scans
```

Request:

```json
{
  "url": "http://127.0.0.1:3000",
  "pattern_ids": ["DP01", "DP02", "DP03"]
}
```

`pattern_ids` is optional. If omitted, all known live fixtures are scanned.

Response:

```json
{
  "scan_id": "live-20261006T085203301009Z",
  "status": "QUEUED",
  "target": "http://127.0.0.1:3000",
  "pattern_ids": ["DP01", "DP02", "DP03"],
  "status_url": "/api/scans/live-...",
  "report_url": "/api/scans/live-.../report"
}
```

### Read scan status

```text
GET /api/scans/{scan_id}
```

Statuses:

```text
QUEUED → RUNNING → COMPLETED
                     └→ FAILED
```

### Read scan history

```text
GET /api/scans
```

### Read evidence

```text
GET /api/scans/{scan_id}/evidence
```

### Read findings

```text
GET /api/scans/{scan_id}/findings
```

### Read the complete report

```text
GET /api/scans/{scan_id}/report
```

### Existing live SSE stream

```text
GET /api/inspection/stream?target=<url>
```

SSE events:

```text
started
stage
finding
classification
complete
error
```

The SSE path remains available for the live inspection screen. The `/api/scans` path is the persistent orchestration path used by the saved-results dashboard.

---

## 9. Evidence and persistence layout

### Live API scan

```text
evidence/live-scans/live-<UTC-timestamp>/
├── screenshots/
│   ├── dp01-false-urgency.png
│   ├── dp02-basket-sneaking.png
│   ├── dp02-after-uncheck.png
│   └── ...
├── dom/
│   ├── product.html
│   ├── product-text.json
│   └── ...
├── scan.json
├── report.json
└── response.json
```

### SQLite

Default location:

```text
evidence/shadowbait.sqlite3
```

Tables:

```text
scans
├── id
├── target_url
├── started_at
├── finished_at
├── status
├── overall_risk
├── risk_level
├── pattern_ids_json
├── report_json
└── error

evidence
├── scan_id
├── pattern_id
├── route
├── selector
├── text
├── screenshot_path
└── element_state_json

findings
├── scan_id
├── pattern_id
├── name
├── severity
├── confidence
├── status
├── detection_source
├── explanation
├── recommendation
├── evidence_json
└── compliance_json
```

Local databases and generated scan folders are ignored by Git. They remain available in the local working copy after a scan.

---

## 10. Saved-results dashboard

After a scan reaches `COMPLETED`, the inspection screen exposes:

```text
OPEN RESULTS DASHBOARD
```

The route is:

```text
/results/<scan_id>
```

The dashboard retrieves the saved report and displays:

- Target URL and scan time
- Overall risk level and numeric risk score
- Captured finding count
- M2 classified finding count
- High/medium/low severity distribution
- Technical compliance principles
- Finding screenshots
- Observed evidence text
- M2 confidence and detection source
- Potential harm
- Ethical recommendation
- Search filter
- Severity filter
- JSON report download

The dashboard uses screenshots embedded in the saved report response, so it can display evidence without exposing a separate static-file server.

---

## 11. Risk scoring model

Implementation:

```text
backend/app/risk/scoring.py
```

Severity weights:

```text
HIGH   = 3.0
MEDIUM = 2.0
LOW    = 1.0
```

Evidence completeness:

```text
VERIFIED  = 1.0
CANDIDATE = 0.5
```

Formula:

```text
finding score = severity weight × confidence × evidence completeness
overall score  = sum of finding scores
```

Risk levels:

```text
0–2.99  LOW
3–5.99  MEDIUM
6+      HIGH
```

The score is intentionally transparent and deterministic. Future calibration should use expert annotations and measured precision/recall rather than treating the prototype score as a legal or regulatory measurement.

---

## 12. Compliance mapping model

Implementation:

```text
backend/app/compliance/mapping.py
```

Each finding receives:

- Category
- Principle
- Description
- Potential harm
- Recommendation
- Status
- Scope metadata
- Source metadata

The mapping is a technical representation of privacy, consent, transparency, and consumer-choice concerns. It is not an automatic legal conclusion.

---

## 13. Dataset and detection design

### Current ground truth

The current prototype uses a self-authored controlled fixture set embedded in Morrow Market. Each fixture provides:

- Pattern ID
- Route
- Stable selector
- Expected visible text
- Expected interaction state
- Expected screenshot
- Human-authored explanation
- Ethical alternative

This is a reproducible benchmark set for pipeline validation, not a large general-purpose machine-learning dataset.

### Current model behavior

The working Morrow Market workflow does not train a neural network. Its primary path is:

```text
DOM/state evidence
        ↓
rule-based detection
        ↓
optional NLP compatibility/inference layer
        ↓
confidence and evidence-backed result
```

The M2 rule engine currently supports False Urgency and Confirm Shaming language. Other fixtures remain available as M1/M3 evidence for structural, visual, pricing, or journey-specific detectors.

### Verification rule

A result should only be marked `VERIFIED` when it has sufficient evidence, including the relevant text/state, selector, page, and screenshot. Otherwise it remains a candidate or scope-specific observation.

### Future dataset format

A future annotated dataset should contain:

```text
screenshot
HTML/DOM
visible text
user journey
pattern label
severity
selector/bounding box
annotator explanation
ethical alternative
```

Evaluation should measure precision, recall, F1, false-positive rate, and inter-annotator agreement.

---

## 14. Standalone scanner

The standalone Member 1 scanner can run without the scan API:

```bash
SHADOWBAIT_URL=http://127.0.0.1:3000 \
python scripts/member1_inspection.py
```

Environment variables:

```text
SHADOWBAIT_URL
SHADOWBAIT_SCAN_ID
SHADOWBAIT_EVIDENCE_DIR
SHADOWBAIT_CHROMIUM_PATH
```

The standalone scanner writes:

```text
evidence/scans/<scan-id>/
evidence/reports/<scan-id>/response.json
evidence/reports/response.json
```

---

## 15. Automated evidence verification

Run a fresh standalone scan and verify its artifacts:

```bash
python scripts/verify_scan_outputs.py \
  --run-scan \
  --url http://127.0.0.1:3000
```

Verify the newest existing scan:

```bash
python scripts/verify_scan_outputs.py
```

Verify a specific scan:

```bash
python scripts/verify_scan_outputs.py \
  --scan-dir evidence/scans/SCAN-20261005T120000Z
```

The verifier checks JSON validity, screenshots, DOM files, referenced paths, summary counts, and required report fields.

---

## 16. Clean-page false-positive test

The clean page is a transparent comparison fixture at:

```text
http://127.0.0.1:3000/clean-page
```

Run:

```bash
SHADOWBAIT_URL=http://127.0.0.1:3000 \
python scripts/clean_page_check.py
```

The test checks:

1. Forbidden dark-pattern selectors are absent.
2. The production M2 rule engine returns zero findings for the clean page text.

Expected result:

```json
{
  "route": "/clean-page",
  "expected_verified_findings": 0,
  "observed_forbidden_selectors": {},
  "m2_findings": [],
  "false_positives": 0,
  "passed": true
}
```

This is a controlled baseline regression test. It does not establish accuracy across all websites.

---

## 17. Validation commands

### Backend tests

```bash
python -m pytest -q tests/backend
```

Current expected result:

```text
72 passed, 67 subtests passed
```

### Python syntax check

```bash
python -m py_compile \
  backend/inspection_server.py \
  backend/app/api/scan_orchestrator.py \
  backend/app/database/repository.py \
  backend/app/risk/scoring.py \
  backend/app/compliance/mapping.py
```

### Frontend build

```bash
cd demo-site
npm run build
cd ..
```

### Full local baseline sequence

```bash
# Terminal 1
cd demo-site
npm run dev -- --port 3000

# Terminal 2, repository root
PYTHONPATH=backend python backend/inspection_server.py

# Terminal 3, repository root
python -m pytest -q tests/backend
SHADOWBAIT_URL=http://127.0.0.1:3000 python scripts/clean_page_check.py
```

Then run the browser inspection from `/inspect` and open the saved dashboard after completion.

---

## 18. Troubleshooting

### Morrow Market does not open

```bash
cd demo-site
npm install
npm run dev -- --port 3000
```

### API does not respond

```bash
PYTHONPATH=backend python backend/inspection_server.py
curl http://127.0.0.1:5050/health
```

### Chromium is missing

```bash
python -m playwright install chromium
```

### A custom Chromium executable is required

```bash
SHADOWBAIT_CHROMIUM_PATH=/path/to/chromium \
PYTHONPATH=backend python backend/inspection_server.py
```

### Dashboard cannot find a scan

Check that the API process is running, the scan ID is exact, and the database path has not changed between scan creation and dashboard loading.

### Screenshots are not visible in VS Code

Inspect:

```text
evidence/live-scans/<scan_id>/screenshots/
evidence/live-scans/<scan_id>/report.json
evidence/live-scans/<scan_id>/response.json
```

Generated folders are ignored by Git intentionally but remain in the local working tree.

### Clean-page test fails

Do not hide the failure by weakening the rule. Inspect the reported selector or M2 result and decide whether the detector or the fixture is incorrect.

---

## 19. Technical limitations and next development areas

Current limitations:

- Scanner routes/selectors are controlled rather than discovered generically.
- M2 language detection covers a limited set of supported patterns.
- Risk weights are prototype defaults and require calibration.
- Compliance mapping is technical and requires human review.
- The dataset is self-authored and controlled.
- The dashboard currently downloads JSON rather than a formatted PDF.

Planned expansion areas:

1. Generic DOM element discovery.
2. Link/form/user-journey crawling.
3. Screenshot bounding boxes and visual annotations.
4. Expanded structural, pricing, and subscription detectors.
5. Multiple clean benchmark websites.
6. Expert annotation and evaluation metrics.
7. Browser-extension inspection overlay.
8. PDF report generation.
9. Scan comparison and CI/CD thresholds.
10. Larger annotated dataset for future ML training.

---

## 20. Related documentation

- `docs/team/Complete_Team_Serial_Workflow.md` — detailed serial implementation workflow.
- `docs/team/Member_1_Working_Flow.md` — scanner and evidence workflow.
- `docs/team/Project_Contract_Freeze_Checklist.md` — shared contracts and checkpoints.
- `evidence/README.md` — evidence layout and artifact verifier instructions.
- `docs/architecture/` — architecture diagram sources and rendered diagrams.

---

## Safety and research note

ShadowBait is a research and demonstration prototype. It does not process real payments, require user authentication, create malware, or make automatic legal determinations. Findings should be reviewed by an appropriate human before being used for legal, compliance, product, or business decisions.
