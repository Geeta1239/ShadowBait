# ShadowBait presentation separation plan

## Scope of this step

This document records the implementation and design direction before application code changes. No frontend or backend behavior is changed in this step.

## Current-state assessment

The repository already contains a working inspection pipeline:

- `demo-site/src/main.jsx` contains both the DarkShop target experience and ShadowBait inspection/results screens.
- `demo-site/src/styles.css` contains one shared visual system, including shopping UI, CCPA lab, inspection UI, results UI, dark mode, and reset controls.
- `backend/inspection_server.py` accepts a target URL, runs Playwright, captures screenshots/DOM/state, emits live events, classifies supported findings, persists reports, and exposes scan endpoints.
- `evidence/` stores screenshots and structured artifacts.
- The current inspection screen derives its target URL from `window.location.origin`, which couples the scanner to the same site that contains the inspection UI.

The core pipeline is valuable and should be preserved. The redesign should primarily separate the two products at the routing, visual, and target-configuration layers.

## Product boundary

### A. DarkShop / Task marketplace demo website

This is the **target website**. It should look like a realistic consumer-facing shopping or task marketplace site and contain the controlled dark-pattern fixtures used by the scanner.

Responsibilities:

- Product/service browsing, cart, checkout, subscription, cancellation, and fixture routes.
- Controlled, self-authored dark-pattern examples for safe reproducible testing.
- Stable selectors and data attributes consumed by the inspection pipeline.
- A distinct commercial visual identity and color palette.
- No ShadowBait inspection controls in the primary customer-facing navigation.

### B. ShadowBait inspection prototype

This is the **software being demonstrated to judges**. It should be a separate web application shell with a technical/security-audit identity.

Responsibilities:

- Accept a target website URL supplied by the presenter.
- Start and monitor an inspection.
- Show pipeline stages and live events.
- Display captured screenshots and structured evidence.
- Show findings, customer harm, ethical fixes, confidence, severity, risk, and compliance mappings.
- Show real-world dark-pattern case studies as context, not as legal conclusions.
- Provide reset/replay and report download controls.

The two products connect through the target URL and the inspection API, not by sharing the same page shell or theme.

## Planned route and application structure

The repository will contain two separately served frontend applications that share the inspection API but do not share a page shell:

```text
demo-site/       DarkShop / TaskNest target website only
prototype/       ShadowBait inspection prototype only
backend/         Shared inspection API, Playwright pipeline, persistence, and reporting
```

The prototype will use the current demo-site CSS language and component patterns as its starting point, while the demo-site will receive its own consumer-facing theme. The existing backend remains shared and is not duplicated.

Prototype routes:

```text
 /                     ShadowBait landing / overview
/inspect              ShadowBait inspection setup + live run
/results/:scanId      ShadowBait saved results dashboard
/case-studies        ShadowBait real-world case studies
/architecture        ShadowBait pipeline and system explanation

Demo-site routes:

 /                     DarkShop target landing page
/demo/product         DarkShop product fixture
/demo/cart            DarkShop cart fixture
/demo/checkout        DarkShop checkout fixtures
/demo/subscribe       DarkShop subscription fixture
/demo/cancel          DarkShop cancellation fixture
/demo/bait-switch     DarkShop bait-and-switch fixture
/demo/interface...    DarkShop interface-interference fixture
/demo/ccpa-lab        DarkShop controlled fixture catalogue
 /clean-page           DarkShop false-positive control
```

If the current public demo URL must keep its existing paths for compatibility, those paths will remain inside `demo-site/`. The prototype will have its own origin/port and will always receive the demo-site URL through an explicit target field. The important requirement is that the target URL is no longer implicitly `window.location.origin`.

## Presenter flow

The intended judge-facing sequence is:

1. Open the ShadowBait landing page.
2. Explain that ShadowBait inspects external web experiences for dark-pattern signals.
3. Open **New Inspection**.
4. Paste the separate DarkShop/demo-site URL into the target field.
5. Start the inspection.
6. Show live pipeline progress: URL accepted → browser opened → routes inspected → evidence captured → patterns classified → risk/report persisted.
7. Open the evidence gallery and show screenshots from the target site.
8. Open results to explain harm, ethical fixes, risk, and compliance mapping.
9. Use the case-study panel to connect the prototype’s detections to documented real-world consumer harm and regulatory action.
10. Return to the architecture view for the implementation explanation.

## ShadowBait prototype design direction

### Design movement

**Editorial security operations / evidence-room interface.** The product should feel like a calm, trustworthy inspection console rather than a consumer storefront.

### Core principles

1. **Evidence first:** screenshots and observable UI state are more prominent than abstract labels.
2. **Traceability:** every result connects to a target URL, route, selector, event, and artifact.
3. **Calm authority:** use restrained color and clear hierarchy instead of alarm-heavy decoration.
4. **Presentation clarity:** each screen should answer one judge question at a time.

### Color philosophy

ShadowBait will intentionally reuse the current demo-site CSS language rather than introducing a new dark security theme. The separation will come from product identity, information hierarchy, and layout—not from changing the established ShadowBait visual language. Use the existing blue for primary actions and evidence, green for verified/completed states, purple for classification and analysis, and restrained amber for review signals. Use red only for high-severity or failed states.

Proposed ShadowBait palette:

- App background: `#F4F6FB`
- Surface: `#FFFFFF`
- Primary blue: `#2272D8`
- Verified green: `#1E9160`
- Classification purple: `#7359BD`
- Review amber: `#DFA020`
- Primary text: `#111827`
- Secondary text: `#5A6475`
- Border: `#E2E8F0`

Typography, buttons, radii, shadows, status pills, and spacing should reuse the current `Manrope` + `DM Mono` system and existing CSS tokens wherever possible.

### Layout paradigm

Use a **left inspection rail + evidence workspace** rather than a centered marketing grid:

- A persistent rail identifies the active phase: Target, Live Scan, Evidence, Findings, Case Studies, Architecture.
- The main workspace uses a wide target summary and a two-column evidence/results layout.
- Use timeline rails, annotated evidence cards, and compact metadata strips as signature structures.

### Signature elements

- **Inspection rail:** numbered stages with live completion markers.
- **Evidence docket:** screenshot cards with route, selector, timestamp, and verification state.
- **Case-study callout:** an amber “why this matters” card linking a prototype pattern to a documented enforcement example.

### Interaction and animation

- Keep transitions short and purposeful: stage changes, evidence card arrival, and progress updates only.
- Use a subtle scan-line or moving progress accent during active inspection.
- Avoid flashy dashboard animations that compete with the screenshots.
- Make replay/reset an explicit, safe action and preserve the last completed report until a new run starts.

### Typography and voice

- Use a sturdy grotesk for headings and a monospaced face for selectors, scan IDs, and event metadata.
- Headline voice: concise and evidence-led.
- Example lines: “Turn a URL into an evidence trail.” and “Observed in the interface. Explained for the reviewer.”

### Brand essence

**ShadowBait is an explainable website-inspection console for finding manipulative interface patterns before they harm people.**

Personality: **forensic, clear, responsible**.

### Wordmark / mark

Use a compact “SB” mark formed from two offset brackets or an eye-shaped inspection frame. It should not resemble the DarkShop “DS” mark.

## Demo-site design direction

The demo website should adopt a clearly separate consumer-facing identity, for example a warm coral / teal task marketplace called **TaskNest** or another neutral name approved during implementation.

- Friendly commercial typography and rounded cards.
- Warm coral, teal, cream, and charcoal palette.
- Consumer navigation focused on Browse, Offers, Cart, and Help.
- Dark-pattern fixtures remain visible and scanner-readable, but the site should not visually announce itself as ShadowBait.
- The site must retain safe-demo disclaimers in an unobtrusive footer or lab-only route.

The demo website should be presented as a deliberately controlled research target, not as the product interface.

## Data and backend changes planned after approval

1. Replace the inspection page’s implicit `window.location.origin` target with a validated URL input and local-storage persistence for the last target.
2. Keep the existing `/api/scans` and SSE contracts where possible.
3. Add a clear target metadata object to scan state and report presentation.
4. Preserve existing screenshot, DOM, evidence, SQLite, risk, compliance, and report formats.
5. Add a reset/replay action that clears only active UI state and does not delete saved evidence.
6. Keep the controlled demo fixtures and stable selectors intact while changing their visual theme.
7. Add case-study content as versioned, source-linked presentation data rather than blending real cases into scanner findings.
8. Clearly label case studies as documented allegations, settlements, or regulatory actions; ShadowBait findings remain technical observations and are not legal determinations.

## Real-world case-study content to incorporate

The case-study section should use a small, source-linked set of examples that map directly to the prototype’s categories:

### Amazon Prime — enrollment and cancellation friction

The FTC’s June 21, 2023 complaint alleged that Amazon used deceptive or coercive interface designs to enroll consumers in automatically renewing Prime subscriptions and made cancellation difficult through a multi-step flow. The source explicitly states that the complaint was an allegation to be decided by the court; the UI should preserve that distinction. This maps to **Subscription Trap**, **Forced Action**, and **Interface Interference**.

Source: [FTC — Amazon Prime action, June 21, 2023](https://www.ftc.gov/news-events/news/press-releases/2023/06/ftc-takes-action-against-amazon-enrolling-consumers-amazon-prime-without-consent-sabotaging-their)

### Epic Games / Fortnite — unwanted in-game charges

In March 2023, the FTC finalized an order requiring Epic Games to pay $245 million for alleged dark-pattern-driven unwanted charges and unauthorized purchases. The order required the money to be used for consumer refunds and prohibited charging through dark patterns without affirmative consent. This maps to **Basket Sneaking**, **Trick Question**, and **Forced Action**.

Source: [FTC — Epic Games order, March 14, 2023](https://www.ftc.gov/news-events/news/press-releases/2023/03/ftc-finalizes-order-requiring-fortnite-maker-epic-games-pay-245-million-tricking-users-making)

### FTC “Bringing Dark Patterns to Light” report — recurring patterns across industries

The FTC’s September 2022 report identifies recurring tactics including disguised advertising, difficult-to-cancel subscriptions, buried terms and junk fees, countdown timers, pre-checked boxes, and privacy-choice steering. This provides the broader rationale for the prototype’s coverage of **False Urgency**, **Drip Pricing**, **Basket Sneaking**, **Subscription Trap**, and **Disguised Advertisement**.

Source: [FTC — Bringing Dark Patterns to Light, September 15, 2022](https://www.ftc.gov/news-events/news/press-releases/2022/09/ftc-report-shows-rise-sophisticated-dark-patterns-designed-trick-trap-consumers)

### Optional additional case cards

The FTC report also references ABCmouse cancellation friction, LendingClub’s buried fee disclosures, and Vizio’s default data collection settings. These can be added as compact secondary cards if the case-study page needs more breadth, but the primary presentation should stay focused on three memorable examples.

## Implementation phases after plan approval

### Phase 1 — Shell separation

Create distinct ShadowBait and demo-site route shells, navigation, labels, and theme tokens while preserving existing backend contracts.

### Phase 2 — Target URL workflow

Add URL input, validation, target persistence, scan start, and explicit target metadata. Remove the implicit same-origin assumption from the presenter workflow.

### Phase 3 — Evidence-led prototype screens

Refactor inspection, results, and reset controls into ShadowBait screens with the inspection rail, live timeline, evidence docket, and results summary.

### Phase 4 — Demo-site visual redesign

Apply the separate TaskNest/marketplace theme to the controlled target routes without changing scanner selectors or fixture behavior.

### Phase 5 — Case studies and architecture explanation

Add source-linked case-study cards and a presentation-friendly architecture page. Keep legal-status labels precise.

### Phase 6 — End-to-end validation

Run the target site and API separately, enter the target URL through ShadowBait, verify screenshots and persisted reports, verify reset/replay, and confirm the two sites have distinct visual identities.

## Guardrails

- No real payments, authentication, malware, or destructive actions.
- Do not claim a scan proves a legal violation.
- Do not alter evidence selectors or fixture semantics without updating scanner tests and documentation.
- Preserve saved reports and artifact paths for reproducibility.
- Keep all case-study sources visible in the UI or linked from the case-study detail view.
