# Morrow Market demo storefront

Morrow Market is the separate normal e-commerce website that ShadowBait inspects.

It is intentionally presented like a regular shopping experience. The dark-pattern behavior is embedded in the customer journey, but the storefront does not explain, label, compare, or analyze those behaviors. All inspection, customer-impact explanation, guidelines, case studies, and ethical alternatives live in the separate ShadowBait platform.

## Run locally

```bash
cd demo-site
npm install
npm run dev -- --port 3000
```

Open `http://localhost:3000`.

## Storefront routes

- `/` — Morrow Market home page
- `/product` — Aster Wireless Headphones product page
- `/cart` — shopping cart
- `/checkout` — normal-looking checkout flow
- `/subscribe` — Morrow Circle membership signup
- `/cancel` — membership settings and cancellation journey
- `/bait-switch` — finish-selection product journey
- `/interface-interference` — membership plan selection
- `/clean-page` — transparent control page

## Scanable customer journeys

The behaviors remain available through ordinary storefront interactions so the inspection pipeline can capture them:

| Journey | Stable evidence | Behavior in the normal UI |
|---|---|---|
| Product page | `#scarcity-text`, `#offer-timer` | Low-stock message beside a countdown |
| Checkout | `#donation`, `#confirm-shaming` | Optional contribution starts selected; decline wording is guilt-oriented |
| Checkout | `data-ccpa-pattern="DRIP_PRICING"`, `#total-price` | Fees appear later in the order summary |
| Membership | `data-ccpa-pattern="SUBSCRIPTION_TRAP"` | Renewal is selected during signup and cancellation is elsewhere |
| Plans | `data-ccpa-pattern="INTERFACE_INTERFERENCE"` | One plan receives stronger visual emphasis |
| Finish selection | `#bait-switch-status` | Offer state can change at the final step |

These selectors and fixtures are implementation evidence for the scanner; they are not presented as labels to storefront visitors.

## Light and dark theme

The store includes a light/dark theme toggle and persists the selection under `morrow-theme`. The visual language is intentionally different from ShadowBait: warm cream surfaces, coral actions, teal accents, and editorial product imagery.

The Arc Task Light and Fold Weekender tiles now use real product photographs referenced from Lamps Plus and Lo & Sons through image search. They are included for this controlled prototype presentation; replace them with licensed or owned photography before public commercial use.

## Safety boundary

This is a controlled prototype. The demo order button never processes payment, and no real account, subscription, or purchase is created.

## Presentation flow

1. Show Morrow Market as a normal website.
2. Copy its URL.
3. Open ShadowBait at `http://localhost:3100`.
4. Enter `http://127.0.0.1:3000` in the inspection console.
5. Start the scan and explain the captured evidence inside ShadowBait.
