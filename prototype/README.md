# ShadowBait platform prototype

ShadowBait is the separate judge-facing platform for inspecting, explaining, and improving dark-pattern behavior found in another website.

The normal Morrow Market storefront lives in `../demo-site`. ShadowBait does not embed that storefront’s explanatory content. Instead, it receives the storefront URL and turns the resulting browser evidence into a review workspace.

## Run locally

From the repository root:

```bash
cd demo-site
npm install
npm run dev -- --port 3000
```

In another terminal:

```bash
cd prototype
npm install
npm run dev -- --port 3100
```

In a third terminal:

```bash
PYTHONPATH=backend python backend/inspection_server.py
```

Open `http://localhost:3100`.

## Judge-facing flow

1. Show the normal Morrow Market storefront.
2. Copy the storefront URL.
3. Open ShadowBait.
4. Enter the target URL on **Inspect**.
5. Watch the live evidence pipeline.
6. Open the saved results and explain customer impact.
7. Use **Interactive Diff** to show the ethical alternative.
8. Use **Guidelines** and **Case Studies** to connect the prototype to responsible review and real-world consequences.

## Platform routes

- `/` — full platform landing page
- `/inspect` — target URL input and live inspection console
- `/results/:scanId` — saved evidence, risk, impact, and ethical alternatives
- `/guidelines` — practical dark-pattern review checklist
- `/diff` — original state versus ethical alternative comparison
- `/case-studies` — source-linked real-world regulatory cases
- `/architecture` — system separation and inspection pipeline

## Theme system

ShadowBait supports light and dark themes and persists the choice under `shadowbait-theme`. Its visual language is intentionally distinct from the target storefront: cool analytical surfaces, blue evidence actions, purple explanation accents, green verified states, and denser review-oriented layouts.

The two products are consistent in interaction quality and theme support, but deliberately different in tone:

| Website | Visual purpose |
|---|---|
| Morrow Market | Warm, editorial, normal e-commerce storefront |
| ShadowBait | Cool, structured, evidence-first inspection platform |

## Case-study boundary

Case-study summaries are source-linked and use careful wording:

- “The regulator alleged” for complaints
- “The order required” for finalized orders
- “The report describes” for broader research findings

The platform’s automated findings are technical observations for human review, not automatic legal conclusions.
