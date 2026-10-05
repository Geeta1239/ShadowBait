# ShadowBait — File-to-File Project Data Flow

## Purpose

This guide explains the project in the exact order data moves through the repository:

```text
React demo website
  → Vite development server
  → inspection API / Playwright + Chromium
  → DOM, text, state, and screenshot evidence
  → scan.json / response.json
  → rule or detection layer
  → backend risk/compliance integration
  → dashboard results
```

It also separates **what is working in the current repository** from **what the team workflow plans to add next**.

---

## 1. The most important architecture clarification

There are currently two related but different paths:

### Path A — Standalone scanner path

File:

```text
scripts/member1_inspection.py
```

This path runs directly from the command line. It visits the known DarkShop routes, captures evidence, and writes:

```text
evidence/scans/<scan-id>/
evidence/reports/<scan-id>/response.json
evidence/reports/response.json
```

### Path B — Live Inspection button path

Files:

```text
demo-site/src/main.jsx
backend/inspection_server.py
demo-site/vite.config.js
```

This path starts when the user clicks **Start Inspection** in the website. The React page opens an EventSource connection to `/api/inspection/stream`. Vite proxies `/api` to the Python inspection server on port `5050`. The server runs Playwright and writes:

```text
evidence/live-scans/live-<timestamp>/
├── screenshots/
├── dom/
├── scan.json
├── report.json
└── response.json
```

The two paths use the same core idea—browser observation plus evidence—but they are separate implementations in the current prototype.

---

## 2. Step 1 — Demo website creation

### Main files

```text
demo-site/package.json
demo-site/src/main.jsx
demo-site/src/styles.css
demo-site/vite.config.js
demo-site/public/assets/headphones-product.jpg
```

### What `package.json` does

`demo-site/package.json` defines the React/Vite application and the commands:

```text
npm run dev       → Vite development server on port 3000
npm run build     → production build
npm run preview   → preview build on port 3000
```

### What `main.jsx` does

`demo-site/src/main.jsx` is the main React entry point. It contains:

- Product constants and prices.
- The route state.
- DarkShop navigation.
- The controlled dark-pattern fixtures.
- The CCPA pattern lab catalog.
- The inspection page.
- The clean comparison page.
- Checkout state such as the donation checkbox and total price.

The route selection occurs in the `App` component:

```text
/                       → product page
/product                → product page
/cart                   → cart page
/checkout               → checkout page
/subscribe              → subscription-start page
/cancel                 → cancellation page
/interface-interference → visual-choice page
/bait-switch            → bait-and-switch page
/ccpa-lab               → pattern catalog
/diff                   → before/after comparison
/inspect                → live inspection page
/clean-page             → false-positive control
```

### Where the dark patterns are defined

The controlled fixtures are created in the page components in `main.jsx` and styled in `styles.css`.

Examples:

```text
#scarcity-text       → “ONLY 2 LEFT!”
#offer-timer         → countdown timer
#donation            → checked optional donation checkbox
#confirm-shaming     → guilt-oriented decline wording
#total-price         → checkout total
```

The page also uses attributes such as:

```html
data-ccpa-pattern="FALSE_URGENCY"
data-ccpa-pattern="SUBSCRIPTION_TRAP"
data-status="VERIFIED"
```

These attributes make the controlled fixture easy to inspect and explain. They are **ground-truth labels in the demo website**, not evidence that an arbitrary external site would expose the same attributes.

### What `styles.css` contributes

`demo-site/src/styles.css` creates the visual conditions that the scanner records, including:

- Scarcity emphasis.
- Countdown presentation.
- Checked add-on presentation.
- Confirm-shaming text.
- Visual emphasis differences between preferred and muted choices.
- Checkout fee presentation.
- Light and dark themes.

The CSS is part of the controlled test environment, not the detection algorithm.

---

## 3. Step 2 — Frontend starts the inspection

### File

```text
demo-site/src/main.jsx
```

### Component

```text
InspectionPage()
```

When the user clicks **Start Inspection**, the function `startInspection()`:

1. Closes any previous EventSource.
2. Clears old progress and findings from React state.
3. Sets the UI to a running state.
4. Reads an optional API override from local storage.
5. Uses the current website origin as the target URL.
6. Opens an EventSource connection to:

```text
/api/inspection/stream?target=<encoded-current-origin>
```

The page listens for these events:

| Event | Meaning | UI result |
|---|---|---|
| `started` | Browser scan has begun | Shows scan metadata and total findings |
| `stage` | A route/selector is being inspected | Updates progress message |
| `finding` | One pattern evidence package is ready | Adds a live finding card |
| `complete` | All findings and files are saved | Shows saved report paths |
| `error` | Browser/API scan failed | Shows an error message |

The React page does not itself inspect the DOM. It receives scan events from the Python service.

---

## 4. Step 3 — Vite forwards `/api` to Python

### File

```text
demo-site/vite.config.js
```

The Vite proxy maps:

```text
http://localhost:3000/api/*
        ↓
http://127.0.0.1:5050/api/*
```

Specifically:

```text
/api    → http://127.0.0.1:5050
/health → http://127.0.0.1:5050
```

This lets the browser call `/api/inspection/stream` on the same origin while the actual scan runs in the Python service.

### Why this matters

The React application is the user-facing controller. The Python service is the browser-automation worker.

```text
React UI = starts scan and displays events
Python API = launches Chromium and performs scan
```

---

## 5. Step 4 — Python inspection service receives the request

### File

```text
backend/inspection_server.py
```

### Server configuration

At startup, the service reads:

```text
INSPECTION_API_HOST       default: 0.0.0.0
INSPECTION_API_PORT       default: 5050
SHADOWBAIT_TARGET_URL     default: http://127.0.0.1:3000
SHADOWBAIT_EVIDENCE_DIR   default: repository/evidence
```

It creates:

```text
evidence/live-scans/
```

### `/health`

The health endpoint returns a small JSON object showing:

- The service is alive.
- The configured target URL.
- The evidence root.

### `/api/inspection/stream`

The stream endpoint:

1. Reads the `target` query parameter.
2. Opens an SSE response.
3. Creates a timestamped `live-<timestamp>` output directory.
4. Sends a `started` event.
5. Calls `run_scan(target)`.
6. Sends `finding` events as each pattern is captured.
7. Writes the final JSON files.
8. Sends a `complete` event.

If an exception occurs, it sends an `error` event rather than silently reporting success.

---

## 6. Step 5 — Playwright launches Chromium

### Files

```text
backend/inspection_server.py
scripts/member1_inspection.py
```

Both use:

```python
from playwright.sync_api import sync_playwright
```

The browser launch supports:

- Playwright’s installed Chromium by default.
- An optional `SHADOWBAIT_CHROMIUM_PATH` override.

The browser context uses approximately:

```text
viewport: 1440 × 1000
color scheme: light
```

This fixed viewport makes screenshots comparable and makes bounding-box evidence reproducible.

---

## 7. Step 6 — Live scan route-by-route flow

### File

```text
backend/inspection_server.py
```

The server has a `FINDINGS` list. Each entry defines:

```text
pattern ID
pattern name
route
selector
explanation
harm
ethical fix
```

For every entry, the server:

1. Sends a `stage` event.
2. Opens the route with `page.goto()`.
3. Waits for `networkidle`.
4. Locates the configured selector.
5. Fails if the selector is missing.
6. Reads visibility and text.
7. Reads tag, checked state, bounding box, and computed styles.
8. Captures a full-page screenshot.
9. Saves the HTML and visible text.
10. Creates a finding record.
11. Sends a `finding` event.

The live scanner currently checks:

```text
DP01 → /product → #scarcity-text
DP02 → /checkout → #donation
DP03 → /checkout → #confirm-shaming
DP05 → /subscribe → subscription pattern container
DP06 → /interface-interference → pattern container
DP07 → /bait-switch → #bait-switch-status
DP08 → /checkout → drip-pricing pattern container
```

### Special safe interactions

#### Basket Sneaking

The server first captures the checked state, then safely unchecks the donation checkbox and captures an after-state screenshot.

```text
checked=true → checked=false
```

It does not submit a form, make a purchase, or perform an external action.

#### Subscription Trap

The server captures the `/subscribe` view, then navigates to `/cancel` and captures the cancellation flow.

```text
/subscribe → /cancel
```

This is how the prototype compares the start path with the cancellation path.

---

## 8. Step 7 — Standalone scanner flow

### File

```text
scripts/member1_inspection.py
```

This is the command-line scanner and is separate from the live SSE service.

### Configuration

It calculates paths relative to the repository:

```text
REPO_ROOT = repository containing scripts/
BASE_URL = SHADOWBAIT_URL or http://127.0.0.1:3000
EVIDENCE_ROOT = SHADOWBAIT_EVIDENCE_DIR or REPO_ROOT/evidence
RUN_ID = SHADOWBAIT_SCAN_ID or UTC timestamp
```

It creates:

```text
evidence/scans/<run-id>/screenshots/
evidence/scans/<run-id>/dom/
evidence/reports/<run-id>/
```

### `visit()` function

The `visit()` function is the central standalone-scan unit:

```text
route
  → page.goto()
  → save_dom()
  → save_page()
  → element_state()
  → append page record to report
```

### `element_state()` function

For a configured selector, the scanner records:

- Present or missing.
- Visible or hidden.
- Enabled or disabled.
- HTML tag.
- Visible text.
- Input value.
- Checked state for checkboxes/radios.
- ARIA label.
- CCPA data attributes.
- Bounding box.
- Computed color, background, and display.

This is the direct answer to “how does the system observe the UI?”

### `save_dom()` function

For every visited page, it saves:

```text
<name>.html
<name>-text.json
<name>-elements.json
```

The HTML is the live DOM after JavaScript has rendered. The text JSON stores visible body text. The elements JSON stores the selector-level state.

### `save_page()` function

It uses Playwright’s full-page screenshot:

```python
page.screenshot(path=str(path), full_page=True)
```

The JSON stores a repository-relative screenshot path.

---

## 9. Step 8 — How the current distinguishing logic works

The current scanner uses **known route and selector checks plus direct state assertions**. It is not currently a general neural classifier.

### DP02 — Basket Sneaking

The strongest current example:

```text
find #donation
read label text
read checked state
read total before
capture screenshot
uncheck safely
capture screenshot after
read total after
```

The evidence supports a candidate when:

```text
visible
AND checked before affirmative action
AND optional add-on
AND adds to the total
```

A normal checkbox is not automatically a dark pattern. Context is required.

### DP01 — False Urgency

The scanner reads:

```text
#scarcity-text
#offer-timer
```

It stores timer text before and after a short wait to demonstrate that the timer changes. The prototype records the evidence; interpretation of whether the urgency is misleading is a policy/detection decision.

### DP03 — Confirm Shaming

The scanner records the exact text from:

```text
#confirm-shaming
```

The exact phrase is preserved in the finding so a reviewer can see why the candidate exists.

### DP05 — Subscription Trap

The scanner captures both:

```text
/subscribe
/cancel
```

The evidence is comparative: easy start versus separate cancellation flow.

### DP06 — Interface Interference

The scanner records the pattern container plus preferred and muted choices. The evidence concerns visual hierarchy and text, not only a hidden DOM property.

### DP07 — Bait and Switch

The scanner records the selected-offer text and the final unavailable/upgrade state from the page.

### DP08 — Drip Pricing

The scanner records the checkout pattern container and fee-related text. The evidence is the presence of later-added charges in the price flow.

---

## 10. Step 9 — Evidence JSON is assembled

### Standalone output

At the end of `scripts/member1_inspection.py`, the report contains:

```json
{
  "scan": {},
  "pages": [],
  "findings": [],
  "checks": [],
  "summary": {}
}
```

It is written to:

```text
evidence/scans/<scan-id>/scan.json
evidence/reports/<scan-id>/response.json
evidence/reports/response.json
```

### Live output

At the end of `backend/inspection_server.py`, the report is written to:

```text
evidence/live-scans/live-<timestamp>/scan.json
evidence/live-scans/live-<timestamp>/report.json
evidence/live-scans/live-<timestamp>/response.json
```

### Finding record meaning

A finding connects four things:

```text
pattern explanation
  + observed text/state
  + exact selector/page
  + screenshot/DOM evidence
```

This is why the result is explainable rather than an unsupported label.

---

## 11. Step 10 — Output verification

### File

```text
scripts/verify_scan_outputs.py
```

This script can either:

```text
verify newest existing scan
```

or:

```text
run a fresh scan and verify it
```

It checks:

- `scan.json` exists and is valid.
- `response.json` exists and is valid.
- At least one non-empty PNG exists.
- DOM files exist.
- Referenced screenshot paths exist.
- Referenced HTML/text/elements files exist.
- Finding count matches the summary.
- Page count matches the summary.
- `response.json` summary equals `scan.json` summary.

A successful result is:

```text
PASS: scan output is complete
```

This verifier is a test of the evidence pipeline, not a test of universal legal accuracy.

---

## 12. Where Member 2 and Member 3 fit

### Declared workflow files

The repository’s team contract assigns:

```text
backend/app/detection/  → Member 2 rules/detection
backend/app/nlp/        → Member 2 NLP/model extension
backend/app/api/        → Member 3 API
backend/app/database/   → Member 3 storage
backend/app/risk/       → Member 3 risk scoring
backend/app/compliance/ → Member 3 compliance mapping
backend/app/reports/    → Member 3 report generation
frontend/               → Member 4 dashboard
```

### Current repository status

Those folders currently contain placeholders such as `.gitkeep`; the complete Member 2/3 production integration is not represented by working modules in the current repository snapshot.

Therefore, the current end-to-end working path is:

```text
DarkShop React UI
  → Vite
  → Python inspection service or standalone scanner
  → screenshots + DOM + JSON evidence
  → live evidence cards / local reports
```

The planned complete path is:

```text
scanner JSON
  → detection rules/NLP
  → FastAPI orchestration
  → risk score
  → compliance mapping
  → database/history
  → final dashboard/report
```

Do not tell judges that FastAPI, SQLite, DeBERTa, risk scoring, or compliance mapping are already running unless those files are implemented and demonstrated by your friends.

---

## 13. What is hard-coded and what is general

### Current controlled parts

```text
known routes
known selectors
known fixture labels
known expected findings
```

Examples:

```text
/product + #scarcity-text
/checkout + #donation
/checkout + #confirm-shaming
```

### Reusable parts

```text
Playwright browser automation
DOM extraction
visible-text extraction
interactive-state extraction
screenshot capture
HTML/text/JSON evidence writing
artifact verification
```

### Future generalization

A real-site scanner would need to discover elements rather than assume these IDs:

```text
crawl or receive arbitrary URL
  → discover pages and links
  → find forms, checkboxes, buttons, prices, timers
  → inspect labels and nearby text
  → compare before/after state
  → generate candidate findings
  → require evidence and confidence
  → send for human/backend review
```

That is the roadmap from a controlled benchmark to a general inspection tool.

---

## 14. One complete explanation you can give the judges

> The project begins with a controlled React website called DarkShop, where we intentionally create known interface fixtures such as a preselected optional donation, scarcity text with a timer, guilt-oriented decline wording, later fees, and difficult cancellation. The Start Inspection button in `demo-site/src/main.jsx` opens an EventSource connection to `/api/inspection/stream`. Vite forwards that request to `backend/inspection_server.py`, which launches Playwright and Chromium. The browser visits the controlled routes and reads the live DOM, visible text, stable selectors, bounding boxes, computed visual state, and interactive state such as whether a checkbox is checked. It then captures full-page screenshots and writes HTML, text JSON, and element-state JSON. The server assembles those observations into `scan.json`, `report.json`, and `response.json`, while the frontend displays progress and findings. The standalone equivalent is `scripts/member1_inspection.py`, which performs the same evidence-first work from the command line and writes to `evidence/scans/` and `evidence/reports/`. The distinguishing logic is currently transparent rule/state logic, not a trained neural network: for example, Basket Sneaking requires an optional add-on checkbox that is selected before affirmative action and affects the total. The `scripts/verify_scan_outputs.py` test then confirms that the JSON, screenshots, DOM files, and references are complete. Member 2’s detection intelligence and Member 3’s backend/risk/compliance integration are the next layers in the team workflow; they must consume this evidence contract rather than recreate browser inspection.

---

## 15. File map summary

| File/folder | Responsibility | Current status |
|---|---|---|
| `demo-site/package.json` | React/Vite commands and dependencies | Working |
| `demo-site/src/main.jsx` | Demo pages, fixtures, route state, inspection UI | Working |
| `demo-site/src/styles.css` | Visual fixture presentation | Working |
| `demo-site/vite.config.js` | `/api` proxy to port 5050 | Working |
| `backend/inspection_server.py` | Live SSE inspection, Playwright, live evidence | Working |
| `scripts/member1_inspection.py` | Standalone scanner and evidence writer | Working |
| `scripts/verify_scan_outputs.py` | Evidence artifact verifier | Working |
| `evidence/scans/` | Standalone scan outputs | Runtime output |
| `evidence/live-scans/` | Live inspection outputs | Runtime output |
| `evidence/reports/` | Standalone response reports | Runtime output |
| `backend/app/detection/` | Planned Member 2 detection modules | Placeholder in current snapshot |
| `backend/app/nlp/` | Planned model/NLP modules | Placeholder in current snapshot |
| `backend/app/api/` | Planned Member 3 API integration | Placeholder in current snapshot |
| `backend/app/risk/` | Planned risk engine | Placeholder in current snapshot |
| `backend/app/compliance/` | Planned compliance mapper | Placeholder in current snapshot |
| `backend/app/database/` | Planned persistence | Placeholder in current snapshot |
| `frontend/` | Planned separate dashboard layer | Placeholder in current snapshot |
| `docs/team/Complete_Team_Serial_Workflow.md` | Team contract and intended sequence | Specification |
| `docs/architecture/DarkPatternGuard_Architecture.d2` | Full intended architecture | Architecture/specification |

> **Bottom line:** The current working core is the controlled website → browser inspection → evidence package → live display/verification path. The general detection model, backend risk/compliance layer, and final dashboard are downstream team layers that must be connected to this evidence contract.
