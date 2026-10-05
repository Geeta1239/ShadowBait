# DarkPatternGuard — Complete Serial Team Workflow

## Purpose

This document gives the team one strict working sequence. Each member must complete the required output and pass the checkpoint before the next dependent step begins.

> **Final product flow:** DarkShop/demo website → scanner → DOM/text/screenshot evidence → pattern detection → backend/risk/compliance → React dashboard → heatmap/report/simulator

---

# 0. Team setup — Everyone

Before writing feature code, all four members must agree on the following.

## 0.1 Freeze the repository structure

```text
DarkPatternGuard/
├── backend/
│   └── app/
│       ├── crawler/       # Member 1
│       ├── detection/     # Member 2
│       ├── nlp/           # Member 2
│       ├── api/           # Member 3
│       ├── database/      # Member 3
│       ├── compliance/    # Member 3
│       └── risk/          # Member 3
├── frontend/              # Member 4
├── demo-site/             # Member 4
├── evidence/              # Member 1 output
├── tests/                 # Everyone
└── docs/                  # Everyone
```

## 0.2 Freeze ownership

| Member | Primary ownership | Main output |
|---|---|---|
| Member 1 | Playwright, Chromium, DOM, screenshots, interaction state | Structured webpage evidence |
| Member 2 | Rules, NLP, DeBERTa, pattern classification | Pattern + confidence |
| Member 3 | FastAPI, database, risk, compliance, integration | Final verified result |
| Member 4 | DarkShop, React UI, dashboard, heatmap, simulator | Judge-ready product |

## 0.3 Freeze the shared result format

Every member must use the same finding structure.

```json
{
  "rule_id": "DP01",
  "name": "Basket Sneaking",
  "severity": "HIGH",
  "confidence": 0.99,
  "status": "CANDIDATE",
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

## 0.4 Freeze the first MVP scope

Implement in this order:

1. Pre-ticked optional checkbox / Basket Sneaking
2. False Urgency
3. Confirm Shaming
4. Misleading Discount
5. Drip Pricing / Hidden Costs
6. Subscription Trap only if the first five are stable

## Gate 0

The team may start implementation only after:

- Folder ownership is agreed.
- JSON format is agreed.
- Evidence file locations are agreed.
- The first rule is agreed: `DP01 — Basket Sneaking`.

---

# 1. Member 4 — Build the controlled DarkShop website first

Member 4 begins the practical sequence because the rest of the team needs a predictable website for testing.

## Step 1.1 — Build the product page

Create a simple working product page containing:

- Product name: Premium Wireless Headphones
- Current price: ₹799
- Original price: ₹4,999
- Discount label: 84% OFF
- Scarcity text: `ONLY 2 LEFT!`
- Timer: `Offer ends in 08:32`
- Buy button

## Step 1.2 — Build the checkout page

Create a checkout page containing:

- Product price: ₹799
- Optional checkbox: `Add ₹50 donation`
- The checkbox must be checked by default.
- Delivery: ₹99
- Platform fee: ₹49
- Handling fee: ₹20
- Total: ₹967
- Confirm-shaming text: `No, I don't want to save money.`

## Step 1.3 — Add basic routes

Minimum routes:

```text
/
/product
/cart
/checkout
```

The product and checkout pages must be accessible without login, payment, or external services.

## Step 1.4 — Add stable selectors

Member 4 must provide stable IDs or test attributes:

```html
<input id="donation" type="checkbox" checked />
<span id="scarcity-text">ONLY 2 LEFT!</span>
<span id="offer-timer">Offer ends in 08:32</span>
<span id="current-price">₹799</span>
<span id="original-price">₹4,999</span>
<button id="buy-now">BUY NOW</button>
```

## Step 1.5 — Provide the test URL and ground truth

Give Member 1:

- Local URL
- Route list
- Expected element selectors
- Expected text
- Expected checkbox state
- Expected screenshots/pages

## Deliverable from Member 4

```text
Working DarkShop website + route list + stable selectors + ground-truth README
```

## Gate 1

Member 1 can begin only when:

- DarkShop opens in a browser.
- Product and checkout pages load.
- The donation checkbox is visibly checked.
- The timer and scarcity text are visible.
- No login or payment is required.

---

# 2. Member 1 — Build the scanner and evidence layer

Member 1 now converts the DarkShop website into structured evidence.

## Step 2.1 — Set up the browser environment

Install and verify:

- Python 3.11
- Playwright
- Chromium
- BeautifulSoup
- lxml
- Pydantic

Create:

```text
backend/app/crawler/
├── playwright_engine.py
├── page_capture.py
├── dom_extractor.py
├── interaction_engine.py
├── structural_rules.py
├── evidence_writer.py
└── schemas.py
```

## Step 2.2 — Implement URL loading

Implement:

```python
async def scan_page(url: str, scan_id: str) -> dict:
    pass
```

The first version must:

1. Validate the URL.
2. Launch Chromium.
3. Open the page.
4. Wait for the page to stabilize.
5. Record requested URL, final URL, title, and status.
6. Save the HTML.
7. Return JSON-safe output.

Handle invalid URLs, navigation timeouts, redirects, DNS errors, and JavaScript pages.

## Step 2.3 — Extract DOM elements

Extract at minimum:

- Buttons
- Checkboxes
- Radio buttons
- Inputs
- Select fields
- Forms
- Links
- Prices
- Discount labels
- Popups/modals
- Timers
- Scarcity/stock indicators
- Visible text

For every important element record:

- Selector
- Tag
- Text
- Visibility
- Enabled/disabled state
- Attributes
- Bounding box
- Page name

## Step 2.4 — Capture interactive states

For every checkbox and radio button, capture:

- `checked`
- `default_checked`
- `disabled`
- `visible`
- `text`
- `selector`
- `page`

For inputs and buttons capture whether they are visible, enabled, required, selected, or pre-filled.

## Step 2.5 — Capture screenshots

Save by scan ID:

```text
evidence/scans/SCAN-001/
├── screenshots/
│   ├── full_page.png
│   ├── product.png
│   ├── cart.png
│   └── checkout.png
├── dom/
│   ├── page.html
│   ├── elements.json
│   └── text.json
└── scan.json
```

Use a fixed viewport such as 1440×900.

## Step 2.6 — Implement DP01: Basket Sneaking

For every visible checkbox:

```text
if checkbox.checked == true
and checkbox is optional
and checkbox is not required for the main action:
    produce DP01 candidate
```

The finding must contain:

- Rule ID
- Pattern name
- Severity
- Confidence
- Status
- Checkbox text
- Selector
- Page
- Screenshot
- Bounding box
- Checkbox state

## Step 2.7 — Implement structural False Urgency signals

Detect and return evidence for:

- Countdown/timer elements
- Scarcity text
- Stock indicators
- Offer-expiration text

Member 1 supplies the evidence. Member 2 decides whether the language is manipulative.

## Deliverable from Member 1

```text
scan_page(url, scan_id) callable function + saved screenshots + DOM files + structured scanner JSON + DP01 evidence
```

## Gate 2

Member 2 can begin only when a test produces:

```text
DarkShop URL
→ Playwright scan
→ checkout DOM
→ #donation found
→ checked = true
→ DP01 candidate
→ checkout.png + selector + text + bounding box
```

A clean page with an unchecked optional checkbox must not produce DP01.

---

# 3. Member 2 — Build detection intelligence

Member 2 begins only after Member 1’s scanner output is stable.

## Step 3.1 — Consume the scanner contract

Member 2 must read, not recreate, the scanner output:

- Visible text
- Element text
- Selectors
- Page names
- Structural signals
- Screenshot references
- Interactive states

## Step 3.2 — Create rule configuration

Create central pattern configuration:

```yaml
DP01:
  name: Basket Sneaking
  method: DOM
  severity: HIGH

DP02:
  name: False Urgency
  method: NLP + DOM
  severity: MEDIUM

DP03:
  name: Confirm Shaming
  method: NLP
  severity: MEDIUM

DP04:
  name: Drip Pricing
  method: PRICE_FLOW
  severity: HIGH

DP05:
  name: Misleading Discount
  method: PRICE_ANALYSIS
  severity: MEDIUM
```

## Step 3.3 — Verify DP01 using scanner evidence

Member 2 should confirm that the DP01 candidate contains enough evidence:

- Optional checkbox
- Checked state
- Add-on or extra cost text
- Page and selector
- Screenshot

Do not replace the scanner evidence. Enrich it and return the same structure.

## Step 3.4 — Implement the keyword baseline for DP02

Start with simple keywords:

```text
only
left
limited
hurry
expires
last chance
act now
```

Use the scanner’s text and timer/scarcity signals.

Example:

```json
{
  "rule_id": "DP02",
  "name": "False Urgency",
  "confidence": 0.80,
  "status": "CANDIDATE",
  "evidence": {
    "text": "ONLY 2 LEFT!",
    "selector": "#scarcity-text",
    "page": "product",
    "screenshot": "product.png"
  }
}
```

## Step 3.5 — Implement Confirm Shaming

Detect language such as:

```text
No, I don't want to save money.
```

Return the exact text and selector as evidence.

## Step 3.6 — Add DeBERTa only after the baseline works

Do not begin with model training. First prove the keyword/rule pipeline.

Then optionally add DeBERTa-v3-base to classify:

- False Urgency
- Confirm Shaming
- Other manipulative language

Compare rule confidence and model confidence. Keep the explanation traceable.

## Step 3.7 — Add pricing pattern logic

After DP01, DP02, and DP03 are stable, implement:

- Misleading discount: compare original and current prices.
- Drip pricing: compare product price with later-added delivery/platform/handling charges.

These rules must use price evidence from Member 1 and should not invent prices.

## Deliverable from Member 2

```text
Detection/rule modules that consume scanner JSON and return findings with pattern, confidence, status, and evidence
```

## Gate 3

Member 3 can begin integration only when:

- DP01 is verified from scanner evidence.
- DP02 works on `ONLY 2 LEFT!` and timer evidence.
- DP03 works on the confirm-shaming sentence.
- Every finding has evidence.
- No evidence means no verified finding.
- Output follows the shared JSON contract.

---

# 4. Member 3 — Build backend, storage, risk, and compliance integration

Member 3 now turns the scanner and detection modules into one backend product.

## Step 4.1 — Create the FastAPI application

Implement these endpoints:

```text
POST /scan
GET  /scan/{id}
GET  /scan/{id}/results
GET  /scan/{id}/evidence
GET  /reports/{id}
GET  /history
```

## Step 4.2 — Implement `POST /scan`

Input:

```json
{
  "url": "http://localhost:3000"
}
```

Execution sequence:

```text
Receive URL
   ↓
Create scan_id
   ↓
Create scan record
   ↓
Call Member 1 scan_page(url, scan_id)
   ↓
Pass scanner JSON to Member 2
   ↓
Collect findings
   ↓
Calculate risk
   ↓
Map compliance category
   ↓
Store result in SQLite
   ↓
Return scan_id/status
```

## Step 4.3 — Add SQLite storage

Store:

- Scan ID
- URL
- Timestamp
- Scan status
- Scanner output path
- Findings
- Risk score
- Risk level
- Evidence references
- Report reference

Use SQLite for the prototype. Do not introduce PostgreSQL before the MVP works.

## Step 4.4 — Implement risk scoring

Use an explainable formula:

```text
Risk contribution = severity weight × confidence
```

Suggested weights:

```text
HIGH = 20
MEDIUM = 10
LOW = 5
```

Use the project levels:

```text
0–30   LOW
31–60  MEDIUM
61–80  HIGH
81–100 CRITICAL
```

The backend must be able to explain how the final score was calculated.

## Step 4.5 — Add compliance mapping

Map each verified finding to the relevant compliance category, for example:

```json
{
  "framework": "CCPA",
  "category": "Basket Sneaking"
}
```

## Step 4.6 — Add report output

Return a complete shared result:

```json
{
  "scan_id": "SCAN-001",
  "url": "http://localhost:3000",
  "timestamp": "2026-10-05T12:00:00Z",
  "risk_score": 78,
  "risk_level": "HIGH",
  "findings": [],
  "evidence": [],
  "compliance": [],
  "recommendations": []
}
```

## Deliverable from Member 3

```text
Working FastAPI backend that accepts a URL, calls scanner and detectors, stores results, calculates risk, and returns the final JSON
```

## Gate 4

Member 4 can connect the dashboard only when this works using a real DarkShop URL:

```text
POST /scan
→ scan_id returned
→ scanner runs
→ DP01/other findings returned
→ risk score returned
→ evidence paths returned
→ result can be retrieved with GET /scan/{id}/results
```

---

# 5. Member 4 — Build the React product experience

Member 4 now connects the working backend to the user interface.

## Step 5.1 — Build the scan form

Create:

- URL input
- Quick/Full scan selection
- Start Scan button
- Validation message

The form calls:

```text
POST /scan
```

## Step 5.2 — Build the scanning-status page

Display these stages:

```text
Fetching webpage
Parsing DOM
Capturing screenshots
Extracting text
Checking pricing
Analyzing checkout
Running detection
Generating evidence
```

## Step 5.3 — Build the results page

Display:

- Risk score
- Risk level
- Number of patterns
- Pattern cards
- Confidence
- Severity
- Status
- Evidence text
- Recommendation

Example cards:

```text
Basket Sneaking — 99% — HIGH
False Urgency — 94% — MEDIUM
Confirm Shaming — 89% — MEDIUM
Misleading Discount — 81% — MEDIUM
Drip Pricing — 96% — HIGH
```

## Step 5.4 — Build the evidence viewer

When a user selects a finding, display:

- Screenshot
- Highlighted bounding box
- Exact DOM selector
- Extracted text
- Why it was flagged
- Compliance category
- Recommended fix

## Step 5.5 — Build the heatmap

Use Member 1’s:

- Screenshot
- Bounding box
- Selector
- Page name
- Finding ID

Do not recalculate detection in React.

## Step 5.6 — Build the ethical UX simulator

Show:

```text
BEFORE                         AFTER
☑ Add ₹50 donation       →     ☐ Add ₹50 donation
No, I don't want              Continue without offer
 to save money
```

## Step 5.7 — Build the dashboard and report

Add:

- Total scans
- Patterns detected
- High-risk scans
- Compliance status
- Risk distribution
- Pattern distribution
- Recent scans
- Report download/view

## Deliverable from Member 4

```text
React application that submits a URL, displays scan progress, shows findings, renders evidence/heatmap, and presents ethical fixes
```

## Gate 5

The frontend is ready for final integration when:

- A user can enter the DarkShop URL.
- Clicking Start Scan calls the backend.
- Results appear without hardcoded findings.
- Evidence opens from the backend paths.
- Heatmap highlights the correct element.
- Before/After simulator uses the detected evidence.

---

# 6. Final integration — Everyone in this exact order

## Step 6.1 — Run the first end-to-end test

```text
Member 4 DarkShop URL
   ↓
Member 3 POST /scan
   ↓
Member 1 Playwright scanner
   ↓
Member 1 DOM + screenshot evidence
   ↓
Member 2 DP01 detection
   ↓
Member 3 risk/compliance/storage
   ↓
Member 4 React results page
```

## Step 6.2 — Verify DP01 first

Do not add all features before this works.

The first demo must show:

```text
#donation checked
→ Basket Sneaking detected
→ screenshot shown
→ checkbox highlighted
→ recommendation shown
```

## Step 6.3 — Add remaining rules one at a time

Use this order:

1. False Urgency
2. Confirm Shaming
3. Misleading Discount
4. Drip Pricing / Hidden Costs
5. Subscription Trap, if time remains

After adding each rule, test the entire pipeline again.

## Step 6.4 — Test negative cases

Use pages with:

- Unchecked optional checkbox
- No checkbox
- Required terms checkbox only
- No timer
- No scarcity text
- Correctly labelled discount
- No hidden charges

The system must not create verified findings without evidence.

## Step 6.5 — Add wow features last

Only after the core scan works, add:

1. Heatmap
2. Evidence viewer
3. Ethical UX copilot
4. Before/After simulator
5. PDF/report output
6. Compliance visualization

---

# 7. Final demonstration sequence

The live demonstration should be performed in this order:

1. Open DarkPatternGuard.
2. Enter the DarkShop URL.
3. Click **Start Scan**.
4. Show the scanning stages.
5. Show the risk score.
6. Show the detected pattern cards.
7. Open **Basket Sneaking**.
8. Display the checkout screenshot.
9. Highlight the checked donation checkbox.
10. Show the selector and evidence text.
11. Show the compliance category.
12. Show the recommended ethical fix.
13. Open the heatmap.
14. Show the Before/After simulator.
15. Open or download the report.

---

# 8. Final definition of done

The project is working properly when all of the following are true:

- Member 4’s DarkShop loads reliably.
- Member 1 can scan it with Playwright.
- DOM, text, interaction state, and screenshots are saved.
- Member 1 detects the checked optional checkbox.
- Member 2 converts scanner evidence into pattern findings.
- Member 3 exposes the complete API and calculates explainable risk.
- Member 4 displays live backend results rather than hardcoded data.
- Findings include evidence, selectors, screenshots, and recommendations.
- A clean page does not produce false verified findings.
- The full flow can be repeated from the UI without manually editing JSON.

> **Most important rule:** Do not build the final dashboard first. Build and verify the pipeline in order: **controlled website → scanner → detection → backend → frontend → visualization**.
