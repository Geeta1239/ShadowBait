# DarkPatternGuard — Project Contract Freeze Checklist

Before implementation starts, the team must agree on every item in this document. Once frozen, members should not independently change these decisions. Any change must be recorded and approved by all members.

---

# 1. Product scope contract

## 1.1 Freeze the MVP

The first working version will detect these patterns in this exact order:

1. **DP01 — Basket Sneaking / Pre-ticked Checkbox**
2. **DP02 — False Urgency**
3. **DP03 — Confirm Shaming**
4. **DP04 — Misleading Discount**
5. **DP05 — Drip Pricing / Hidden Costs**
6. **DP06 — Subscription Trap**, only if the first five are stable

## 1.2 Freeze what is not part of the first version

Do not implement initially:

- Browser extension
- Mobile application
- Authentication and user roles
- Real payment processing
- Websites requiring login, OTP, or personal data
- Production-scale PostgreSQL
- Real-time continuous monitoring
- All regulatory frameworks
- Training a large multimodal model
- Complex cloud deployment

## 1.3 Freeze the primary demo

The primary demonstration target is the controlled **DarkShop** website.

The first end-to-end demo must prove:

```text
DarkShop URL
→ Playwright scan
→ checked donation checkbox found
→ DP01 detected
→ evidence displayed
→ risk score generated
→ ethical fix displayed
```

---

# 2. Team ownership contract

| Area | Owner | Must not be changed by |
|---|---|---|
| DarkShop demo website | Member 4 | Other members without agreement |
| Playwright/Chromium scanner | Member 1 | Other members |
| DOM and text extraction | Member 1 | Other members |
| Screenshot and interaction capture | Member 1 | Other members |
| Structural scanner rules | Member 1 | Other members |
| Rule engine | Member 2 | Other members |
| NLP/DeBERTa classification | Member 2 | Other members |
| Pattern confidence | Member 2 | Other members |
| FastAPI routes | Member 3 | Other members |
| Scan orchestration | Member 3 | Other members |
| SQLite/database | Member 3 | Other members |
| Risk scoring | Member 3 | Other members |
| Compliance mapping | Member 3 | Other members |
| React frontend | Member 4 | Other members |
| Dashboard/heatmap/simulator | Member 4 | Other members |
| Tests and documentation | Everyone | No one works in isolation |

## 2.1 Ownership rule

No member may directly modify another member’s module without agreement. Integration must happen through the frozen interfaces below.

---

# 3. Repository and branch contract

## 3.1 Freeze the repository structure

```text
DarkPatternGuard/
├── README.md
├── .env.example
├── .gitignore
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── api/             # Member 3
│       ├── crawler/         # Member 1
│       ├── detection/       # Member 2
│       ├── nlp/             # Member 2
│       ├── database/        # Member 3
│       ├── risk/            # Member 3
│       ├── compliance/      # Member 3
│       └── reports/         # Member 3
├── frontend/                # Member 4
├── demo-site/               # Member 4
├── evidence/                # Scanner artifacts
├── tests/
│   ├── scanner/             # Member 1
│   ├── detection/           # Member 2
│   ├── backend/             # Member 3
│   ├── frontend/            # Member 4
│   └── integration/         # Everyone
└── docs/
```

## 3.2 Freeze branch and merge rules

Recommended:

```text
main       = stable/demo-ready code
member-1   = scanner work
member-2   = detection/NLP work
member-3   = backend/integration work
member-4   = frontend/demo-site work
```

Rules:

- Never commit broken code directly to `main`.
- Each member must include tests with feature changes.
- Merge only after the relevant checkpoint passes.
- Tag each stable milestone, for example `v0.1-dp01`.

---

# 4. Technology contract

Freeze the first-version technology stack:

| Layer | Decision |
|---|---|
| Frontend | React + Vite |
| Styling | Tailwind CSS |
| Components | ShadCN UI, if needed |
| Charts | Recharts |
| Backend | Python 3.11 + FastAPI |
| Validation | Pydantic |
| Browser automation | Playwright + Chromium |
| HTML parsing | BeautifulSoup + lxml |
| NLP baseline | Keyword/rule matching |
| NLP model | DeBERTa-v3-base, optional after baseline |
| Database | SQLite |
| Evidence storage | Local `evidence/` directory |
| Diagram/source documentation | Markdown + D2/Mermaid |

Do not switch technologies during the MVP unless the team explicitly approves it.

---

# 5. Environment contract

## 5.1 Freeze local ports

Recommended:

```text
Frontend:  http://localhost:5173
Backend:   http://localhost:8000
DarkShop:  http://localhost:3000
```

## 5.2 Freeze environment variables

Create `.env.example`:

```text
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
DEMO_SITE_URL=http://localhost:3000
EVIDENCE_DIR=./evidence
DATABASE_URL=sqlite:///./darkpattern_guard.db
BROWSER_TIMEOUT_MS=30000
BROWSER_VIEWPORT_WIDTH=1440
BROWSER_VIEWPORT_HEIGHT=900
```

Never commit secrets or personal credentials.

## 5.3 Freeze startup commands

Document the exact commands:

```bash
# Backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev -- --port 5173

# Demo site
cd demo-site
npm install
npm run dev -- --port 3000
```

---

# 6. API contract

Member 3 owns these endpoints. The endpoint names and methods must not change without team approval.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/scan` | Start a scan |
| GET | `/scan/{id}` | Get scan status |
| GET | `/scan/{id}/results` | Get final results |
| GET | `/scan/{id}/evidence` | Get evidence metadata |
| GET | `/reports/{id}` | Get report data |
| GET | `/history` | Get previous scans |

## 6.1 `POST /scan` request

```json
{
  "url": "http://localhost:3000",
  "mode": "full"
}
```

Allowed `mode` values:

```text
quick
full
```

The team must decide whether `mode` is required. Recommended: default to `full` for the hackathon demo.

## 6.2 `POST /scan` response

```json
{
  "scan_id": "SCAN-001",
  "status": "QUEUED"
}
```

Allowed status values:

```text
QUEUED
RUNNING
COMPLETED
FAILED
```

## 6.3 Error response

Every endpoint must use a consistent error shape:

```json
{
  "error": {
    "code": "SCAN_TIMEOUT",
    "message": "The webpage did not load within the allowed time.",
    "scan_id": "SCAN-001"
  }
}
```

Freeze error codes before implementation.

---

# 7. Scanner contract — Member 1 to the team

## 7.1 Scanner function

```python
async def scan_page(url: str, scan_id: str) -> dict:
    """Open a URL and return structured evidence."""
```

## 7.2 Scanner responsibilities

The scanner must:

- Open the URL using Chromium.
- Save final URL and page title.
- Extract live DOM data.
- Extract visible text.
- Capture interactive states.
- Capture screenshots.
- Detect structural signals.
- Save evidence by scan ID.
- Return JSON-serializable output.

## 7.3 Scanner output

```json
{
  "scan_id": "SCAN-001",
  "url": "http://localhost:3000",
  "timestamp": "2026-10-05T12:00:00Z",
  "success": true,
  "pages_scanned": ["product", "checkout"],
  "dom_summary": {
    "buttons": 3,
    "checkboxes": 1,
    "radio_buttons": 0,
    "forms": 1,
    "links": 8,
    "prices": 5,
    "timers": 1,
    "popups": 0
  },
  "elements": [],
  "visible_text": [],
  "interactive_states": [],
  "structural_findings": [],
  "screenshots": []
}
```

## 7.4 Evidence location

```text
evidence/scans/{scan_id}/
├── screenshots/
├── dom/
└── scan.json
```

---

# 8. Finding contract — Member 2 to Member 3

Every finding must have these fields:

```json
{
  "rule_id": "DP01",
  "name": "Basket Sneaking",
  "severity": "HIGH",
  "confidence": 0.99,
  "status": "VERIFIED",
  "source": "DOM_RULE",
  "evidence": {
    "text": "Add ₹50 donation",
    "selector": "#donation",
    "page": "checkout",
    "screenshot": "checkout.png",
    "bounding_box": {
      "x": 220,
      "y": 530,
      "width": 180,
      "height": 24
    }
  }
}
```

Allowed severity values:

```text
LOW
MEDIUM
HIGH
```

Allowed status values:

```text
CANDIDATE
VERIFIED
REJECTED
```

Allowed source values:

```text
DOM_RULE
STRUCTURAL_RULE
KEYWORD_RULE
NLP_MODEL
PRICE_ANALYSIS
FUSED
```

## 8.1 Evidence rule

A finding cannot be marked `VERIFIED` unless it contains:

- Exact text or element state
- Selector
- Page name
- Screenshot reference
- At least one reason for the detection

---

# 9. Pattern rules contract

Freeze the rule definitions before coding.

| Rule ID | Pattern | Primary input | Owner | Severity |
|---|---|---|---|---|
| DP01 | Basket Sneaking | Checked optional checkbox | M1 + M2 | HIGH |
| DP02 | False Urgency | Timer + scarcity text + NLP | M1 + M2 | MEDIUM |
| DP03 | Confirm Shaming | Manipulative rejection text | M2 | MEDIUM |
| DP04 | Drip Pricing | Price flow and added fees | M2 + M3 | HIGH |
| DP05 | Misleading Discount | Original/current price analysis | M2 + M3 | MEDIUM |
| DP06 | Subscription Trap | Signup/cancellation flow | M1 + M2 + M3 | HIGH |

## 9.1 DP01 definition

Flag when:

- A checkbox is visible.
- It is already checked.
- It is optional.
- It adds a product, service, donation, or cost.
- Evidence shows the selector, text, page, and checked state.

## 9.2 DP02 definition

Create a candidate when:

- A timer, expiry signal, scarcity label, or stock indicator exists.
- The relevant text is extracted.
- The selector and screenshot are available.

Member 2 decides whether the language qualifies as false urgency.

---

# 10. Evidence contract

Every evidence item must be traceable from the result screen back to the source webpage.

Minimum evidence fields:

```text
scan_id
page
url
selector
text
screenshot
bounding_box
captured_at
source_module
```

## 10.1 Screenshot contract

Required names:

```text
full_page.png
product.png
cart.png
checkout.png
```

Use a fixed viewport:

```text
width: 1440
height: 900
```

## 10.2 Evidence retention

For the prototype:

- Keep evidence in the local `evidence/` directory.
- Do not upload user websites or personal data to external storage.
- Do not scan pages requiring login or OTP.
- Do not submit forms, make payments, or perform destructive actions.

---

# 11. Risk and compliance contract

## 11.1 Risk calculation

Use an explainable score:

```text
Risk contribution = severity weight × confidence
```

Weights:

```text
HIGH = 20
MEDIUM = 10
LOW = 5
```

Risk levels:

```text
0–30   LOW
31–60  MEDIUM
61–80  HIGH
81–100 CRITICAL
```

The exact behavior when the score exceeds 100 must be frozen. Recommended: cap the score at 100.

## 11.2 Compliance result

```json
{
  "framework": "CCPA",
  "category": "Basket Sneaking",
  "explanation": "An optional paid add-on was selected by default.",
  "recommendation": "Leave the optional checkbox unchecked."
}
```

The team must agree whether the prototype uses CCPA only or displays multiple frameworks. Recommended: use CCPA only for the first demo.

---

# 12. Frontend contract

Member 4 must use backend responses rather than hardcoded findings.

Required pages/components:

1. Home / landing
2. New scan form
3. Scanning progress
4. Results dashboard
5. Evidence viewer
6. Heatmap
7. Ethical UX simulator
8. Reports/history

The frontend must consume:

```text
scan_id
status
risk_score
risk_level
findings
evidence
compliance
recommendations
```

The frontend must never independently recalculate detection or risk.

---

# 13. Security and safety contract

The scanner must:

- Scan only URLs entered for this project.
- Avoid login pages, OTP, payment, and personal data.
- Never submit a real order.
- Never store credentials.
- Use timeouts and maximum page limits.
- Sanitize filenames using `scan_id`.
- Avoid executing destructive actions.
- Return a safe error when a page is inaccessible.

---

# 14. Testing contract

Before moving to the next stage, each member must provide tests.

## Member 1 tests

- Valid URL loads.
- Invalid URL fails cleanly.
- HTML is saved.
- Checkbox state is captured.
- Timer is found.
- Screenshot is saved.
- DP01 is detected only when appropriate.

## Member 2 tests

- Keyword urgency is detected.
- Confirm shaming is detected.
- Clean wording is not falsely flagged.
- Confidence is between `0.0` and `1.0`.
- Every verified finding includes evidence.

## Member 3 tests

- `POST /scan` accepts a valid URL.
- Scan status changes correctly.
- Results are stored in SQLite.
- Risk score is explainable.
- Error response format is consistent.

## Member 4 tests

- URL form submits correctly.
- Progress screen renders.
- Live results render.
- Evidence opens correctly.
- Heatmap uses actual bounding boxes.
- No detection is hardcoded in the UI.

## Integration tests

The full system must pass:

```text
DarkShop URL
→ POST /scan
→ scanner output
→ detector output
→ risk/compliance output
→ frontend result
```

---

# 15. Definition-of-done contract

The MVP is considered complete only when:

- The DarkShop website loads.
- A URL can be scanned from the React UI.
- Playwright captures DOM and screenshots.
- DP01 is detected correctly.
- At least DP02 and DP03 are detected after DP01.
- Backend results are stored and retrievable.
- Risk score is explainable.
- Evidence is displayed in the frontend.
- Heatmap highlights the detected element.
- Ethical recommendation is shown.
- A clean page does not produce false verified findings.
- The team can repeat the demo without manually editing JSON.

---

# 16. Approval table

Each member should approve these items before implementation.

| Contract item | Member 1 | Member 2 | Member 3 | Member 4 | Frozen date |
|---|---:|---:|---:|---:|---|
| MVP pattern list | ☐ | ☐ | ☐ | ☐ | |
| Repository structure | ☐ | ☐ | ☐ | ☐ | |
| Technology stack | ☐ | ☐ | ☐ | ☐ | |
| Ports and environment variables | ☐ | ☐ | ☐ | ☐ | |
| API endpoints | ☐ | ☐ | ☐ | ☐ | |
| Scanner JSON | ☐ | ☐ | ☐ | ☐ | |
| Finding JSON | ☐ | ☐ | ☐ | ☐ | |
| Evidence format | ☐ | ☐ | ☐ | ☐ | |
| Risk formula | ☐ | ☐ | ☐ | ☐ | |
| Compliance scope | ☐ | ☐ | ☐ | ☐ | |
| Safety boundaries | ☐ | ☐ | ☐ | ☐ | |
| Testing gates | ☐ | ☐ | ☐ | ☐ | |
| Definition of done | ☐ | ☐ | ☐ | ☐ | |

> **Implementation should begin only after this approval table is complete.**
