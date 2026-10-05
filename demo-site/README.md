# DarkShop Demo Website

Controlled test website for the ShadowBaitSentinel/DarkPatternGuard scanner.

## Run locally

```bash
cd demo-site
npm install
npm run dev
```

Open:

- http://localhost:3000/
- http://localhost:3000/product
- http://localhost:3000/cart
- http://localhost:3000/checkout

## Scanner ground truth

| Pattern | Expected evidence | Stable selector |
|---|---|---|
| Basket Sneaking | Optional donation checkbox is checked by default | `#donation` |
| False Urgency | Scarcity text and countdown timer | `#scarcity-text`, `#offer-timer` |
| Misleading Discount | Current/original price and discount label | `#current-price`, `#original-price`, `#discount-label` |
| Drip Pricing | Delivery, platform, and handling fees appear at checkout | `#total-price` and `.order-line` |
| Confirm Shaming | Guilt-oriented rejection wording | `#confirm-shaming` |

## Important test state

On `/checkout`:

```text
#donation.checked === true
label text = Add ₹50 donation
confirm-shaming text = No, I don't want to save money.
```

This is a controlled demo only. The Place Demo Order button never submits a real order or payment.
