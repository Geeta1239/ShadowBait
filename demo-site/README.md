# DarkShop CCPA Pattern Lab

Controlled test website for the ShadowBaitSentinel/DarkPatternGuard scanner.

This site intentionally contains clearly labelled, simulated dark-pattern fixtures for scanner development. It is not a legal conclusion or a real checkout.

## Run locally

```bash
cd demo-site
npm install
npm run dev
```

Open:

- http://localhost:3000/ — product flow with the 3 verified findings
- http://localhost:3000/product — product page
- http://localhost:3000/cart — cart
- http://localhost:3000/checkout — checkout with Basket Sneaking and Confirm Shaming
- http://localhost:3000/ccpa-lab — coverage catalogue
- http://localhost:3000/diff — interactive rule/evidence/customer-harm/ethical-fix comparison
- http://localhost:3000/diff — interactive rule/evidence/customer-harm/ethical-fix comparison
- http://localhost:3000/subscribe — Subscription Trap fixture
- http://localhost:3000/cancel — cancellation-flow fixture
- http://localhost:3000/bait-switch — Bait and Switch fixture

## Current CCPA coverage

| CCPA category | Demo status | Main evidence |
|---|---|---|
| False Urgency | VERIFIED | `#scarcity-text`, `#offer-timer` |
| Basket Sneaking | VERIFIED | `#donation` is checked by default |
| Confirm Shaming | VERIFIED | `#confirm-shaming` |
| Forced Action | SIMULATED | CCPA Lab fixture |
| Subscription Trap | SIMULATED | `/subscribe` → `/cancel` |
| Interface Interference | SIMULATED | CCPA Lab fixture |
| Bait and Switch | SIMULATED | `/bait-switch`, `#bait-switch-status` |
| Drip Pricing | CANDIDATE | Checkout fees and `#total-price` |
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

The site also shows an ethical Before → After alternative for the three verified patterns.

## Safety boundary

The Place Demo Order button never submits a real order or payment. The Rogue Malware category is intentionally not implemented. All other CCPA Lab entries are safe, non-malicious UI fixtures for scanner development.


## Interactive diff page

`/diff` is the primary presentation page for the project demo. Select any of the 13 CCPA categories to animate a three-step chain:

```text
CCPA rule → observed evidence → customer harm
```

Use **Ethical fix view** to switch the same chain to the remediated interface and customer benefit. Verified, candidate, simulated, and excluded statuses are shown separately.


## Interactive diff page

`/diff` is the primary presentation page for the project demo. Select any of the 13 CCPA categories to animate a three-step chain:

```text
CCPA rule → observed evidence → customer harm
```

Use **Ethical fix view** to switch the same chain to the remediated interface and customer benefit. Verified, candidate, simulated, and excluded statuses are shown separately.
