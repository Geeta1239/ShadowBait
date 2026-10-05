# DarkShop CCPA Pattern Lab

Controlled test website for the ShadowBaitSentinel/DarkPatternGuard scanner.

This site intentionally contains clearly labelled, safe dark-pattern fixtures for scanner development. Seven categories are verified within this controlled demo, five remain simulated fixtures, and Rogue Malware is excluded. It is not a legal conclusion or a real checkout.

## Run locally

```bash
cd demo-site
npm install
npm run dev
```

Open:

- http://localhost:3000/ — product flow with the 7 verified findings
- http://localhost:3000/product — product page
- http://localhost:3000/cart — cart
- http://localhost:3000/checkout — checkout with Basket Sneaking and Confirm Shaming
- http://localhost:3000/ccpa-lab — coverage catalogue
- http://localhost:3000/diff — interactive rule/evidence/customer-harm/ethical-fix comparison
- http://localhost:3000/inspect — visible Member 1 inspection demo with live progress, captured screenshots, and CCPA explanations
- http://localhost:3000/subscribe — Subscription Trap fixture
- http://localhost:3000/cancel — cancellation-flow fixture
- http://localhost:3000/bait-switch — Bait and Switch fixture
- http://localhost:3000/interface-interference — Interface Interference fixture

## Current CCPA coverage

| CCPA category | Demo status | Main evidence |
|---|---|---|
| False Urgency | VERIFIED | `#scarcity-text`, `#offer-timer` |
| Basket Sneaking | VERIFIED | `#donation` is checked by default |
| Confirm Shaming | VERIFIED | `#confirm-shaming` |
| Forced Action | SIMULATED | CCPA Lab fixture |
| Subscription Trap | VERIFIED | `/subscribe` → `/cancel` |
| Interface Interference | VERIFIED | `/interface-interference` |
| Bait and Switch | VERIFIED | `/bait-switch`, `#bait-switch-status` |
| Drip Pricing | VERIFIED | Checkout fees, `data-ccpa-pattern="DRIP_PRICING"`, and `#total-price` |
| Disguised Advertisement | SIMULATED | CCPA Lab fixture |
| Nagging | SIMULATED | CCPA Lab fixture |
| Trick Question | SIMULATED | CCPA Lab fixture |
| SaaS Billing | SIMULATED | CCPA Lab fixture |
| Rogue Malware | EXCLUDED | No malware-like behavior is created for safety |

## Verified product-flow evidence

On `/product`:

```text
#scarcity-text = ONLY 2 LEFT!
#offer-timer = countdown
```

On `/checkout`:

```text
#donation.checked === true
label text = Add ₹50 donation
#confirm-shaming = No, I don't want to save money.
```

The site also shows ethical Before → After alternatives for the seven verified patterns. Each verified fixture has visible evidence text, stable selectors or data attributes, and a route that Member 1 can scan.

## Safety boundary

The Place Demo Order button never submits a real order or payment. The Rogue Malware category is intentionally not implemented. All other CCPA Lab entries are safe, non-malicious UI fixtures for scanner development.


## Interactive diff page

`/diff` is the primary presentation page for the project demo. Select any of the 13 CCPA categories to animate a three-step chain:

```text
CCPA rule → observed evidence → customer harm
```

Use **Ethical fix view** to switch the same chain to the remediated interface and customer benefit. Verified, candidate, simulated, and excluded statuses are shown separately.


## Dark mode and product image

The header includes a **Dark / Light** toggle. The selected theme is stored in `localStorage` under `shadowbait-theme`, so it persists after reloads and across the product, checkout, CCPA Lab, and interactive diff pages.

The product page uses the bundled real headphone photograph at `public/assets/headphones-product.jpg`. It is loaded locally through `/assets/headphones-product.jpg`, so the demo does not depend on an external image host during testing.
