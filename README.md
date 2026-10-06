# ShadowBait

## Explainable dark-pattern inspection and ethical UX auditing prototype

ShadowBait is a controlled research prototype that inspects a demo shopping website, captures browser evidence, classifies supported dark-pattern language, calculates an explainable risk score, maps findings to privacy and consumer-choice principles, stores scan history in SQLite, and presents the result in a React dashboard.

> **Important scope statement:** ShadowBait is currently a controlled prototype validated against the DarkShop demo fixtures. It is not legal advice, it does not make an automatic legal determination, and it is not yet a fully generic crawler for every arbitrary public website.

---

## 1. One-minute project explanation

```text
DarkShop demo website
        ↓
Playwright + Chromium inspection
        ↓
DOM, visible text, state, and screenshot evidence
        ↓
M2 rule/NLP classification for supported language patterns
        ↓
Explainable severity and confidence risk scoring
        ↓
CCPA/dark-pattern principle mapping and recommendation
        ↓
SQLite scan history + JSON evidence package
        ↓
React results dashboard
```

The simplest explanation for a judge is:

> **ShadowBait uses browser automation to capture evidence of suspicious interface patterns, applies explainable rules to supported text, calculates a transparent risk score, attaches an ethical recommendation, and shows the complete result with screenshots in a dashboard.**

---

## 2. Current implementation status

| Workflow stage | Current status | Main implementation |
|---|---|---|
| Build controlled DarkShop website | Complete | `demo-site/` |
| Inspect website with Playwright | Complete for controlled fixtures | `backend/inspection_server.py`, `scripts/member1_inspection.py` |
| Save screenshots and evidence | Complete | `evidence/live-scans/`, `evidence/scans/` |
| Connect M1 evidence to M2 | Complete for supported language patterns | `backend/app/integration/m1_m2_adapter.py` |
| Scan orchestration API | Complete | `POST/GET /api/scans` in `backend/inspection_server.py` |
| SQLite persistence | Complete | `backend/app/database/repository.py` |
| Risk scoring | Complete | `backend/app/risk/scoring.py` |
| Compliance mapping and recommendations | Complete as technical mapping | `backend/app/compliance/mapping.py` |
| Final results dashboard | Complete for saved reports | `demo-site/src/main.jsx` route `/results/<scan_id>` |
| Clean-page false-positive baseline | Complete | `scripts/clean_page_check.py` |
| Generic arbitrary-site crawling | Future work | Not yet the current prototype scope |
| Full ML training dataset | Future work | No neural network is trained by the current demo |
| PDF audit report | Future enhancement | JSON download currently available |

The latest implementation has been validated with:

```text
72 backend tests passed
67 backend subtests passed
Frontend production build passed
Full seven-pattern scan completed
Clean-page false positives: 0
Dashboard browser smoke test passed
```

---

## 3. Repository structure

```text
ShadowBait/
├── backend/
│   ├── inspection_server.py          # HTTP API, SSE stream, Playwright orchestration
│   └── app/
│       ├── api/
│       │   └── scan_orchestrator.py # request validation and in-memory lifecycle store
│       ├── compliance/
│       │   └── mapping.py            # technical principle/harm/recommendation mapping
│       ├── database/
│       │   └── repository.py          # SQLite schema and persistence
│       ├── detection/
│       │   ├── evidence_engine.py
│       │   ├── fusion.py
│       │   ├── models.py
│       │   ├── pattern_detector.py
│       │   ├── rule_engine.py
│       │   └── rules_config.py
│       ├── integration/
│       │   └── m1_m2_adapter.py       # scanner evidence → M2 contract
│       ├── nlp/
│       │   └── ...                    # preprocessing and optional inference API
│       └── risk/
│           └── scoring.py              # explainable risk calculation
├── demo-site/
│   ├── src/main.jsx                   # DarkShop pages, inspection UI, dashboard
│   ├── src/styles.css                 # UI and dashboard styles
│   ├── public/                        # static assets
│   ├── vite.config.js                 # Vite + /api proxy to port 5050
│   └── package.json
├── docs/
│   ├── architecture/                  # architecture sources and diagrams
│   ├── judge-guide/                   # judge-facing explanations and file flow
│   └── team/                          # serial workflow and ownership contract
├── evidence/
│   ├── README.md                      # evidence layout and verifier instructions
│   ├── member1-step2/                 # checked-in reference evidence
│   └── live-scans/                    # generated live API scans; ignored by Git
├── scripts/
│   ├── member1_inspection.py          # standalone scanner
│   ├── verify_scan_outputs.py         # scanner artifact verifier
│   └── clean_page_check.py             # clean-page false-positive integration test
├── tests/
│   ├── backend/                       # detection, API, DB, risk, compliance tests
│   ├── integration/                   # integration-test location
│   ├── scanner/
│   └── frontend/
├── requirements.txt
└── README.md
```

### Team ownership

| Owner | Responsibility | Main folders |
|---|---|---|
| Member 1 | Browser inspection, DOM, screenshots, state evidence | `backend/inspection_server.py`, `scripts/`, `evidence/` |
| Member 2 | Rules, NLP, pattern classification | `backend/app/detection/`, `backend/app/nlp/` |
| Member 3 | API orchestration, database, risk, compliance | `backend/app/api/`, `database/`, `risk/`, `compliance/` |
| Member 4 | DarkShop website, React inspection screen, dashboard | `demo-site/` |
| Everyone | Tests, documentation, final integration | `tests/`, `docs/`, `README.md` |

---

## 4. Prerequisites

Install:

- Python 3.11 or newer
- Node.js 18 or newer
- npm
- Git
- Chromium through Playwright

Python dependency:

```text
playwright>=1.40,<2
```

The project currently does not require a paid API, database server, login, payment, or external website.

---

## 5. First-time installation

### 5.1 Clone and enter the repository

```bash
git clone https://github.com/Geeta1239/ShadowBait.git
cd ShadowBait
```

### 5.2 Install Python dependencies

Recommended on macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

If PowerShell blocks activation, run the commands from Command Prompt or use:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m playwright install chromium
```

### 5.3 Install the DarkShop frontend

```bash
cd demo-site
npm install
cd ..
```

---

## 6. Run the complete local demo

Use two terminals from the repository root.

### Terminal 1 — DarkShop website

```bash
cd demo-site
npm run dev -- --port 3000
```

Open:

```text
http://localhost:3000/product
http://localhost:3000/inspect
http://localhost:3000/clean-page
```

### Terminal 2 — inspection and orchestration API

Activate the virtual environment first, then run:

```bash
PYTHONPATH=backend python backend/inspection_server.py
```

The API listens on:

```text
http://127.0.0.1:5050
```

Health check:

```bash
curl http://127.0.0.1:5050/health
```

Expected response shape:

```json
{
  "ok": true,
  "target": "http://127.0.0.1:3000",
  "evidence_root": "evidence",
  "orchestration_api": true
}
```

The Vite development server forwards `/api/*` requests to port `5050` through `demo-site/vite.config.js`.

---

## 7. Normal browser demonstration flow

1. Open `http://localhost:3000/product`.
2. Explain that DarkShop is a controlled test website with intentional fixtures.
3. Open `http://localhost:3000/inspect`.
4. Click **START INSPECTION**.
5. Watch the live event log as routes and selectors are inspected.
6. Watch screenshots and evidence cards appear.
7. Wait for the scan to reach `7/7`.
8. Click **OPEN RESULTS DASHBOARD**.
9. Review the risk score, severity distribution, screenshots, M2 results, compliance mapping, and recommendations.
10. Use **DOWNLOAD JSON REPORT** if a machine-readable report is required.

The dashboard URL has this format:

```text
http://localhost:3000/results/<scan_id>
```

Example:

```text
http://localhost:3000/results/live-20261006T085203301009Z
```

The `scan_id` is different for every scan.

---

## 8. The seven controlled verified fixtures

| Scanner ID | Pattern | Route | Evidence selector | Current owner |
|---|---|---|---|---|
| `DP01` | False Urgency | `/product` | `#scarcity-text` plus timer | M1 evidence + M2 language classification |
| `DP02` | Basket Sneaking | `/checkout` | `#donation` | M1/M3 structural evidence |
| `DP03` | Confirm Shaming | `/checkout` | `#confirm-shaming` | M2 language classification |
| `DP05` | Subscription Trap | `/subscribe` | `[data-ccpa-pattern="SUBSCRIPTION_TRAP"]` | M1/M3 flow evidence |
| `DP06` | Interface Interference | `/interface-interference` | `[data-ccpa-pattern="INTERFACE_INTERFERENCE"]` | M1/M3 visual evidence |
| `DP07` | Bait and Switch | `/bait-switch` | `#bait-switch-status` | M1/M3 flow evidence |
| `DP08` | Drip Pricing | `/checkout` | `[data-ccpa-pattern="DRIP_PRICING"]` | M1/M3 price-flow evidence |

The current M2 language detector specifically supports:

- False Urgency
- Confirm Shaming

The other verified fixtures are still captured as browser evidence and included in risk/compliance reporting. Their dedicated structural, pricing, or flow detectors are future expansion areas.

Additional CCPA lab entries are simulated or intentionally excluded to make the test scope explicit. They are not part of the seven-pattern live scanner list.

---

## 9. Direct scan API

### Start a scan

```bash
curl -X POST http://127.0.0.1:5050/api/scans \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:3000"}'
```

You can limit the scan to selected known patterns:

```bash
curl -X POST http://127.0.0.1:5050/api/scans \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:3000","pattern_ids":["DP01","DP02","DP03"]}'
```

The response is asynchronous:

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

```bash
curl http://127.0.0.1:5050/api/scans/<scan_id>
```

Possible statuses:

```text
QUEUED
RUNNING
COMPLETED
FAILED
```

### List saved scan history

```bash
curl http://127.0.0.1:5050/api/scans
```

### Read evidence

```bash
curl http://127.0.0.1:5050/api/scans/<scan_id>/evidence
```

### Read classified findings

```bash
curl http://127.0.0.1:5050/api/scans/<scan_id>/findings
```

### Read the complete report

```bash
curl http://127.0.0.1:5050/api/scans/<scan_id>/report
```

### Backward-compatible live SSE endpoint

The existing live inspection UI uses:

```text
GET /api/inspection/stream?target=<url>
```

SSE events include:

```text
started
stage
finding
classification
complete
error
```

---

## 10. Evidence and output locations

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

### Standalone scanner

```text
evidence/scans/<scan-id>/
├── screenshots/
├── dom/
└── scan.json

evidence/reports/<scan-id>/response.json
evidence/reports/response.json
```

Generated scan folders and local databases are ignored by Git. They remain visible in the local VS Code repository after a scan, but they are not committed automatically.

The live API database is normally:

```text
evidence/shadowbait.sqlite3
```

The database is ignored by Git.

---

## 11. Standalone scanner

The standalone scanner is useful when you want the Member 1 evidence package without starting the full API.

Start DarkShop first, then run from the repository root:

```bash
SHADOWBAIT_URL=http://127.0.0.1:3000 \
python scripts/member1_inspection.py
```

Useful environment variables:

```text
SHADOWBAIT_URL                 Target website URL
SHADOWBAIT_SCAN_ID             Stable custom scan ID
SHADOWBAIT_EVIDENCE_DIR        Custom evidence root
SHADOWBAIT_CHROMIUM_PATH       Optional explicit Chromium executable
```

The scanner uses Playwright’s installed Chromium by default. Do not use old hard-coded paths from another machine.

---

## 12. Automated evidence verification

To run a fresh standalone scan and verify its artifacts:

```bash
python scripts/verify_scan_outputs.py \
  --run-scan \
  --url http://127.0.0.1:3000
```

To verify the newest existing standalone scan:

```bash
python scripts/verify_scan_outputs.py
```

To verify a specific scan:

```bash
python scripts/verify_scan_outputs.py \
  --scan-dir evidence/scans/SCAN-20261005T120000Z
```

The verifier checks:

- `scan.json`
- `response.json`
- PNG screenshots
- DOM files
- referenced evidence paths
- summary counts
- JSON validity

A successful run prints:

```text
PASS: scan output is complete
```

---

## 13. Clean-page false-positive test

The clean comparison page is intentionally transparent and should produce no dark-pattern finding.

Run the integration check while the demo website is active:

```bash
SHADOWBAIT_URL=http://127.0.0.1:3000 \
python scripts/clean_page_check.py
```

The test validates both layers:

1. Forbidden dark-pattern selectors are absent from `/clean-page`.
2. The production M2 rule engine returns zero findings for the page’s visible text.

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

This is a baseline accuracy check, not proof of universal accuracy on all websites.

---

## 14. Test and build commands

### Backend tests

From the repository root:

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

### Frontend production build

```bash
cd demo-site
npm run build
cd ..
```

### Dashboard browser smoke test

After completing a scan, open:

```text
http://localhost:3000/results/<scan_id>
```

Confirm that the page shows:

- `Inspection results dashboard`
- overall risk level
- risk score
- at least one screenshot
- finding name
- compliance recommendation

---

## 15. Risk scoring

The scoring implementation is in:

```text
backend/app/risk/scoring.py
```

The prototype uses:

```text
finding score = severity weight × confidence × evidence completeness
```

Weights:

```text
HIGH   = 3
MEDIUM = 2
LOW    = 1
```

Evidence completeness:

```text
VERIFIED  = 1.0
CANDIDATE = 0.5
```

Risk-level thresholds:

```text
0–2.99  LOW
3–5.99  MEDIUM
6+      HIGH
```

The complete report includes:

```json
{
  "risk": {
    "risk_score": 16.8,
    "risk_level": "HIGH",
    "verified_findings": 7,
    "candidate_findings": 0,
    "high_severity_findings": 3,
    "medium_severity_findings": 4,
    "low_severity_findings": 0,
    "scored_findings": []
  }
}
```

The score is explainable prototype logic. It should be calibrated with expert annotations and real interface data before being treated as a production compliance metric.

---

## 16. Compliance mapping

The mapping implementation is in:

```text
backend/app/compliance/mapping.py
```

Each captured finding receives:

- Pattern category
- Choice/privacy principle
- Description
- Potential user harm
- Ethical recommendation
- Verification status
- Technical-review scope
- Source label

The report intentionally states:

```text
technical mapping for human review; not a legal determination
```

This distinction must be preserved in presentations and judge discussions.

---

## 17. Dataset and model explanation

### What dataset does the current prototype use?

The current prototype uses a **self-authored controlled ground-truth fixture set** embedded in DarkShop. Each fixture has:

- Known pattern ID
- Known route
- Stable selector
- Expected visible text
- Expected state
- Expected screenshot
- Human-authored explanation
- Ethical alternative

This is a benchmark/validation fixture set, not a large production training dataset.

### Is a neural network being trained?

No neural network is trained by the current DarkShop demo workflow.

The current working detection path is:

```text
DOM/state evidence from M1
        ↓
rule-based M2 detectors for supported language patterns
        ↓
optional NLP compatibility/inference layer
        ↓
confidence and evidence-backed finding
```

Future ML work would require a real annotated interface dataset containing screenshots, DOM, text, user journeys, pattern labels, severity, evidence selectors, and expert explanations.

### How is a checkbox distinguished from a dark pattern?

The system does not label every checkbox as a dark pattern. It checks evidence such as:

```text
Is the checkbox visible?
Is it optional?
Is it preselected?
Does it add an extra charge or consent action?
Is the selector and page recorded?
Is a screenshot available?
```

A verified result requires evidence. The clean-page test provides a baseline against false positives.

---

## 18. Judge-facing limitations

State these limitations honestly:

1. DarkShop is a controlled validation website, not a random real-world site.
2. The scanner currently uses a controlled list of known fixtures and selectors.
3. M2 currently classifies supported language patterns rather than every pattern type.
4. The risk score is explainable prototype logic, not a legal or regulatory score.
5. The compliance mapping supports human review; it does not declare a legal violation.
6. The current ground truth is self-authored and should be expanded with expert annotations.
7. A browser extension, generic crawler, public-site benchmark, and PDF report are future enhancements.

A strong response to “What is this useful for if it is not fully generic yet?” is:

> **The controlled site gives us repeatable ground truth, reliable evidence capture, and measurable regression tests. It lets us validate the complete pipeline before introducing the complexity and safety risks of arbitrary public websites. The same pipeline is designed to accept generic DOM and journey evidence in the next phase.**

---

## 19. Troubleshooting

### The website does not open

```bash
cd demo-site
npm install
npm run dev -- --port 3000
```

Check:

```text
http://127.0.0.1:3000/product
```

### The API cannot be reached

Start it from the repository root:

```bash
PYTHONPATH=backend python backend/inspection_server.py
```

Check:

```bash
curl http://127.0.0.1:5050/health
```

### Playwright cannot find Chromium

```bash
python -m playwright install chromium
```

If a specific browser must be used:

```bash
SHADOWBAIT_CHROMIUM_PATH=/path/to/chromium \
PYTHONPATH=backend python backend/inspection_server.py
```

### The dashboard says the scan was not found

Check that:

1. The API process is still running.
2. The `scan_id` is copied exactly.
3. The scan was created by the same API database.
4. The database path was not changed between scan and dashboard load.

### Screenshots are not visible in VS Code

Run a fresh scan and inspect:

```text
evidence/live-scans/<scan_id>/screenshots/
evidence/live-scans/<scan_id>/report.json
evidence/live-scans/<scan_id>/response.json
```

The generated folders are ignored by Git intentionally, but they should exist locally.

### The clean-page test fails

Run it with the correct target:

```bash
SHADOWBAIT_URL=http://127.0.0.1:3000 \
python scripts/clean_page_check.py
```

If it reports a selector or M2 finding, inspect the output before changing the detector. A false-positive regression should be investigated, not hidden.

---

## 20. Safe development rules

- Do not add real payment processing.
- Do not create malware or malicious downloads.
- Do not present technical mappings as legal conclusions.
- Do not claim a model was trained when it was not.
- Do not commit generated scan databases or local evidence runs.
- Keep screenshots, selectors, and text attached to every verified finding.
- Keep the clean-page baseline test passing.
- Run backend tests and the frontend build before pushing.
- Use a separate branch for substantial future work.

---

## 21. Recommended next enhancements

The current foundation is ready for the next research/product phase:

1. Generic DOM element discovery beyond fixed fixtures.
2. User-journey crawling across links and forms.
3. Screenshot bounding boxes and evidence annotations.
4. Multi-page clean benchmarks and expert annotation workflow.
5. Precision, recall, F1, and inter-annotator agreement reporting.
6. PDF audit report generation.
7. Browser extension for real-time page overlays.
8. Scan comparison and CI/CD risk thresholds.
9. Expanded M2 detectors for structural, pricing, and subscription patterns.
10. A real annotated dataset for future ML training.

---

## 22. Project documentation

- `docs/judge-guide/ShadowBait_Judge_Ready_Prototype_Guide.md` — judge-facing architecture and dataset/model explanation.
- `docs/judge-guide/ShadowBait_File_to_File_Data_Flow.md` — source-file-to-source-file data flow.
- `docs/team/Complete_Team_Serial_Workflow.md` — detailed seven-step team workflow.
- `docs/team/Member_1_Working_Flow.md` — scanner and evidence workflow.
- `docs/team/Project_Contract_Freeze_Checklist.md` — shared contract and checkpoint rules.
- `evidence/README.md` — exact runtime artifact layout and output verifier usage.

---

## License and research note

This repository is a research and demonstration prototype for ethical UX and dark-pattern inspection. Review all findings with a qualified human reviewer before making a legal, regulatory, or business decision.
