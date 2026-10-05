# DarkPatternGuard — Member 1 Working Flow

## 1. Your role

You are the **Scanner Engineer**. Your job is to reliably inspect a real webpage and return structured, evidence-backed data to the rest of the system.

> **Your core output:** Website URL → browser scan → structured webpage evidence

You own:

- Playwright + Chromium browser automation

- URL loading and page navigation

- DOM extraction

- Text and interactive-element extraction

- Screenshot capture

- Interactive-state capture

- Structural dark-pattern detection

- Evidence packaging for Member 2 and Member 3

You do **not** own:

- DeBERTa/NLP classification — Member 2

- Risk scoring, compliance mapping, database, or FastAPI integration — Member 3

- React dashboard, heatmap UI, or demo site — Member 4

Your scanner should be callable by the backend. Member 3 will connect it to `POST /scan`.

---

## 2. Overall working flow

```
Input URL
   ↓
Validate URL
   ↓
Launch Playwright + Chromium
   ↓
Open webpage and wait for stable state
   ↓
Capture page metadata
   ↓
Extract DOM elements
   ├── buttons
   ├── checkboxes
   ├── radio buttons
   ├── forms and inputs
   ├── prices and discount labels
   ├── links
   ├── popups/modals
   ├── timers/countdowns
   └── visible text
   ↓
Capture interactive states
   ├── checked/unchecked
   ├── enabled/disabled
   ├── selected options
   └── visible/hidden
   ↓
Capture screenshots
   ├── full page
   ├── product page
   ├── cart page
   └── checkout page
   ↓
Run structural rules
   ├── pre-ticked checkbox
   ├── countdown/timer
   ├── scarcity/stock indicator
   └── supporting structural evidence for pricing
   ↓
Create evidence bundle
   ↓
Return standard scanner JSON
   ↓
Member 2 performs language/AI detection
   ↓
Member 3 performs risk, compliance, storage, and API integration
```

---

## 3. Freeze the interface before coding

Before implementation, agree with the team on the scanner function and JSON shape. Do not invent a separate response format.

### Recommended scanner function

```python
async def scan_page(url: str, scan_id: str) -> dict:
    """Open a 6webpage and return structured evidence."""
```

The function should:

1. Receive a URL and scan ID.

1. Perform the browser scan.

1. Save screenshots and DOM evidence under the scan directory.

1. Return a serializable dictionary.

1. Never return a verified finding without evidence.

### Suggested evidence directory

```
evidence/
└── scans/
    └── SCAN-001/
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

---

## 4. Module structure

Create or own the following modules inside `backend/crawler/`:

```
backend/
└── app/
    └── crawler/
        ├── __init__.py
        ├── playwright_engine.py
        ├── page_capture.py
        ├── dom_extractor.py
        ├── interaction_engine.py
        ├── structural_rules.py
        ├── evidence_writer.py
        └── schemas.py
```

### Responsibility of each file

| File | Responsibility |
| --- | --- |
| `playwright_engine.py` | Launch Chromium, create context/page, navigate, handle timeouts |
| `page_capture.py` | Capture full-page and page-state screenshots |
| `dom_extractor.py` | Extract HTML, visible text, selectors, and relevant DOM elements |
| `interaction_engine.py` | Read checkbox/radio/input/button states and safe page states |
| `structural_rules.py` | Detect pre-ticked checkboxes, timers, scarcity, and stock indicators |
| `evidence_writer.py` | Save HTML, JSON, screenshots, and evidence metadata |
| `schemas.py` | Pydantic/dataclass models for scanner output |

Member 3 may place API routes elsewhere, but should call your scanner rather than duplicate browser logic.

---

## 5. Detailed implementation sequence

## Phase 1 — Environment and browser setup

### Step 1: Prepare the Python environment

Install and verify:

- Python 3.11

- Playwright

- Chromium browser

- BeautifulSoup

- lxml

- Pydantic

Example setup:

```bash
cd DarkPatternGuard/backend
python -m venv .venv
source .venv/bin/activate
pip install playwright beautifulsoup4 lxml pydantic
playwright install chromium
```

Use a `.env.example` for configurable values such as:

```
EVIDENCE_DIR=./evidence
BROWSER_TIMEOUT_MS=30000
SCREENSHOT_FULL_PAGE=true
```

### Step 2: Implement a minimal URL loader

The first successful test should do only this:

```
URL → Chromium → page title + final URL + HTML
```

The loader must handle:

- Invalid URL

- DNS failure

- Navigation timeout

- HTTP errors

- Redirects

- JavaScript-rendered content

- Pages that do not finish loading

Use a timeout and return a structured error instead of crashing the backend.

Example result:

```json
{
  "success": true,
  "url_requested": "http://localhost:3000",
  "url_final": "http://localhost:3000/",
  "title": "DarkShop",
  "status_code": 200
}
```

---

## Phase 2 — DOM and text extraction

### Step 3: Save the raw page

After navigation:

1. Save the final URL.

1. Save the page title.

1. Save the complete HTML to `dom/page.html`.

1. Save visible text separately.

1. Record the timestamp and page type if known.

Do not rely only on BeautifulSoup. Use Playwright for the live DOM because JavaScript may modify the page after the initial HTML response.

### Step 4: Generate stable selectors

Every extracted element should have a selector or an equivalent locator reference.

Selector priority:

1. Unique `id`

1. Stable `data-testid` or `data-*` attribute

1. Unique name attribute

1. Form-associated selector

1. CSS path fallback

Avoid selectors based only on unstable generated class names when possible.

Example:

```json
{
  "selector": "#donation",
  "tag": "input",
  "type": "checkbox",
  "text": "Add ₹50 donation"
}
```

### Step 5: Extract the required DOM categories

Extract at minimum:

- Buttons

- Checkboxes

- Radio buttons

- Text inputs

- Select fields

- Forms

- Links

- Prices

- Currency symbols

- Discount labels

- Popups and modal dialogs

- Countdown/timer elements

- Stock/scarcity indicators

- Visible text blocks

For each element, record:

```json
{
  "selector": "button.buy-now",
  "tag": "button",
  "role": "button",
  "text": "Buy Now",
  "visible": true,
  "enabled": true,
  "bounding_box": {
    "x": 420,
    "y": 680,
    "width": 120,
    "height": 42
  },
  "attributes": {
    "id": "",
    "class": "buy-now",
    "name": "",
    "type": "button"
  }
}
```

Bounding boxes are important later for the heatmap, even though Member 4 owns the UI.

---

## Phase 3 — Interactive-state capture

### Step 6: Capture form-control state

For every checkbox, radio button, and select field, record the current state.

For checkboxes:

```json
{
  "selector": "#donation",
  "type": "checkbox",
  "checked": true,
  "default_checked": true,
  "disabled": false,
  "visible": true,
  "text": "Add ₹50 donation",
  "page": "checkout"
}
```

For radios:

```json
{
  "selector": "input[name='delivery'][value='express']",
  "type": "radio",
  "checked": true,
  "group": "delivery",
  "text": "Express delivery"
}
```

For buttons and inputs, record whether they are:

- Visible

- Enabled

- Disabled

- Required

- Selected

- Pre-filled

### Step 7: Do not make destructive interactions

The scanner should be evidence-first and safe.

Do not:

- Submit a real payment form

- Enter personal information

- Log in to a user account

- Accept irreversible terms

- Make a purchase

- Send messages

- Delete data

For the prototype, use the controlled DarkShop website and safe navigation only. If a page requires login, mark it as inaccessible instead of trying to bypass it.

---

## Phase 4 — Screenshot capture

### Step 8: Capture the required screenshots

At minimum capture:

```
full_page.png
product.png
cart.png
checkout.png
```

If the URL contains only one page, still save `full_page.png` and use the relevant page name in metadata.

Each screenshot record should include:

```json
{
  "filename": "checkout.png",
  "page": "checkout",
  "url": "http://localhost:3000/checkout",
  "viewport": {
    "width": 1440,
    "height": 900
  },
  "full_page": true
}
```

Use a consistent viewport across scans so the evidence and heatmap are comparable.

Recommended default:

```
width: 1440
height: 900
```

Take the screenshot after the page is stable and after any safe navigation required to reach the page state.

---

## Phase 5 — Member 1 structural detections

## Detection 1: Pre-ticked checkbox / basket sneaking

This is your first and most important detection.

### Detection logic

```
For each visible checkbox:
    if checked == true:
        if it is optional and not required for the core action:
            create candidate DP01 finding
            attach selector, text, page, screenshot, and bounding box
```

Do not flag a checkbox as basket sneaking if it is clearly required for the primary action, such as accepting mandatory terms where no optional add-on is involved.

### Candidate finding

```json
{
  "rule_id": "DP01",
  "name": "Basket Sneaking",
  "severity": "HIGH",
  "confidence": 0.99,
  "status": "CANDIDATE",
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
    },
    "state": {
      "checked": true,
      "disabled": false,
      "visible": true
    }
  }
}
```

Member 3/Member 2 may later change `CANDIDATE` to `VERIFIED` after the complete detection/evidence pipeline. If your rule has sufficient evidence, the team may agree to mark this DOM-only rule as verified immediately.

## Detection 2: Structural false-urgency evidence

Member 2 owns language interpretation. You own the structural evidence.

Search the live DOM for:

- Countdown elements

- Timer attributes or timer-like IDs/classes

- Text containing stock indicators

- Text containing scarcity indicators

- Visible “expires” or offer-end metadata

Examples of structural evidence:

```json
{
  "rule_id": "DP02",
  "name": "False Urgency",
  "status": "CANDIDATE",
  "source": "DOM_STRUCTURAL_RULE",
  "evidence": {
    "text": "Only 2 left!",
    "selector": ".stock-warning",
    "page": "product",
    "screenshot": "product.png",
    "signals": ["scarcity_text"]
  }
}
```

Do not decide whether the wording is manipulative using only this layer. Send the text and structural signals to Member 2 for NLP interpretation.

---

## Phase 6 — Evidence bundle creation

### Step 9: Write one scan result

At the end of a scan, write:

- `scan.json`

- `page.html`

- `elements.json`

- `text.json`

- Screenshots

The scanner result should be serializable and contain no browser objects.

### Recommended scanner result

```json
{
  "scan_id": "SCAN-001",
  "url": "https://darkshop.local",
  "timestamp": "2026-10-04T20:00:00Z",
  "scanner": {
    "success": true,
    "browser": "chromium",
    "final_url": "https://darkshop.local",
    "title": "DarkShop",
    "pages_scanned": ["product", "cart", "checkout"]
  },
  "screenshots": [
    "evidence/scans/SCAN-001/screenshots/full_page.png",
    "evidence/scans/SCAN-001/screenshots/product.png",
    "evidence/scans/SCAN-001/screenshots/cart.png",
    "evidence/scans/SCAN-001/screenshots/checkout.png"
  ],
  "dom_summary": {
    "buttons": 3,
    "checkboxes": 1,
    "radio_buttons": 0,
    "forms": 1,
    "links": 8,
    "prices": 5,
    "popups": 0,
    "timers": 1
  },
  "elements": [],
  "visible_text": [],
  "interactive_states": [],
  "structural_findings": []
}
```

The final top-level contract used by the whole application can then wrap your scanner output inside the shared `findings` contract used by Member 3.

---

## 6. Team integration flow

### Your handoff to Member 2

Send:

- All visible text blocks

- Text associated with each DOM element

- Page name

- Selector

- Screenshot path

- Bounding box

- Structural signals such as `timer`, `scarcity`, or `stock_indicator`

Member 2 uses this input for keyword rules and DeBERTa classification.

### Your handoff to Member 3

Send:

- `scan_page(url, scan_id )` callable interface

- Scanner JSON schema

- Evidence directory convention

- Error response format

- List of structural findings

- Example scan output

- Unit and integration tests

Member 3 should call the scanner from the backend flow:

```
POST /scan
   ↓
Member 3 creates scan_id
   ↓
Member 3 calls Member 1 scan_page(url, scan_id)
   ↓
Member 1 returns structured evidence
   ↓
Member 2 analyzes text/evidence
   ↓
Member 3 combines findings, calculates risk, stores result
```

### Your handoff to Member 4

Provide:

- Screenshot paths or URLs

- Element selectors

- Bounding boxes

- Finding-to-element mapping

- Evidence text

- Page names

This allows the frontend to render the heatmap and evidence viewer without re-running the browser scan.

---

## 7. Development milestones

### Milestone 1 — Browser inspection works

You can demonstrate:

```
Give me a URL → I open it with Playwright → I return title, URL, HTML, and visible text
```

Acceptance criteria:

- Chromium launches successfully.

- Valid pages are loaded.

- Invalid URLs return structured errors.

- Navigation timeout is handled.

- Raw HTML is saved.

- A basic JSON result is returned.

### Milestone 2 — DOM extraction works

Acceptance criteria:

- Buttons, inputs, checkboxes, radios, forms, links, prices, popups, and text are extracted.

- Every relevant element has a selector.

- Visible/enabled/checked state is captured.

- Bounding boxes are recorded.

- `elements.json` is saved.

### Milestone 3 — Screenshots and evidence work

Acceptance criteria:

- Full-page screenshot is saved.

- Product/cart/checkout screenshots are supported.

- Screenshot metadata is returned.

- Evidence is grouped by scan ID.

- A finding can point to a selector and screenshot.

### Milestone 4 — First detection works

Use DarkShop and demonstrate:

```
DarkShop URL
   ↓
Playwright
   ↓
Checkout DOM
   ↓
#donation is checked
   ↓
DP01 candidate finding
   ↓
Screenshot + selector + text + state
```

This must work before adding additional rules.

### Milestone 5 — Structural urgency evidence works

Acceptance criteria:

- Countdown/timer elements are detected.

- Scarcity/stock text is extracted.

- Evidence is attached to the exact element.

- Member 2 can consume the result for language classification.

### Milestone 6 — Integration is complete

Acceptance criteria:

- Member 3 can call your scanner from `POST /scan`.

- Member 2 receives the expected text/evidence format.

- Member 4 can display the screenshot and locate the finding by selector/bounding box.

- The complete first end-to-end demo shows the pre-ticked checkbox finding.

---

## 8. Testing plan

Create tests under `tests/scanner/`.

### Unit tests

Test:

- URL validation

- Selector generation

- Visible text extraction

- Price extraction

- Checkbox state extraction

- Timer detection

- Scarcity text detection

- Evidence file writing

- Error formatting

### Integration tests

Use the controlled DarkShop demo site.

Test that:

1. The product page is captured.

1. The checkout page is captured.

1. `#donation` is found.

1. `checked == true` is returned.

1. `DP01` is produced.

1. `checkout.png` exists.

1. The evidence contains a selector and text.

1. The output can be serialized to JSON.

### Negative tests

Use a clean page with:

- No optional checkbox

- An unchecked donation checkbox

- A required terms checkbox

- No timer

- No scarcity text

The scanner should not create false DP01 findings for these cases.

### Reliability tests

Also test:

- Slow page

- Empty page

- Redirected page

- Missing selector

- Hidden checkbox

- Disabled checkbox

- Multiple checkboxes

- Multiple pages

- Page with a modal popup

---

## 9. Recommended implementation order

Do not build all features at once. Follow this exact order:

1. Launch Chromium.

1. Load one URL.

1. Return title, final URL, and HTML.

1. Extract visible text.

1. Extract buttons and form controls.

1. Capture checkbox states.

1. Save a full-page screenshot.

1. Save evidence by scan ID.

1. Detect one pre-ticked optional checkbox.

1. Run the detection against DarkShop.

1. Connect the scanner to Member 3’s backend.

1. Add product/cart/checkout capture.

1. Add timer and scarcity structural signals.

1. Add robust selectors and bounding boxes.

1. Add tests and documentation.

1. Only then support extra detection categories.

---

## 10. Definition of done

Member 1 is complete when the following demo works without manual inspection:

```
Input: DarkShop URL

1. Playwright opens the site.
2. The scanner captures the product and checkout states.
3. DOM elements are extracted.
4. The donation checkbox is found as checked.
5. A DP01 candidate/verified finding is produced.
6. The finding contains:
   - rule ID
   - pattern name
   - severity
   - confidence
   - text
   - selector
   - page
   - screenshot
   - bounding box
   - checkbox state
7. The screenshot and DOM files are saved.
8. The JSON can be consumed by Members 2, 3, and 4.
9. A clean page does not produce a false finding.
10. Errors are returned as structured JSON instead of crashing.
```

### Final responsibility statement

> **Member 1 owns Playwright, Chromium, DOM extraction, screenshots, interaction state, and structural detection. The deliverable is a reliable evidence-producing scanner that turns a website into structured data for the rest of DarkPatternGuard.**

