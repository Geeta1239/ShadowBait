"""Builds the labeled text dataset for the M2 NLP classifier.

Edit the three lists below (add REAL phrases from real shopping sites!) and re-run:
    python ml/nlp/make_dataset.py
Outputs ml/nlp/data/{all,train,val,test}.csv  (70/15/15 split, stratified, fixed seed).

HONEST NOTE: the seed examples were written by hand, not scraped. A model scored on
them looks better than it will on the real web. Add real examples before you report numbers.
"""
import csv
import os
import random
import re

FALSE_URGENCY = [
    "Only 2 left in stock!", "Hurry, only 3 rooms left at this price!", "Offer ends in 08:32",
    "Sale ends tonight at midnight", "Last chance to grab this deal", "Limited stock available",
    "Act now before it's too late!", "12 people are viewing this right now", "Selling fast - almost gone!",
    "Limited time offer: 50% off today only", "Time is running out!", "Don't miss out on this exclusive deal",
    "Only 1 seat remaining on this flight", "Deal expires in 10 minutes", "Hurry! Offer ends soon",
    "Grab it before it's gone forever", "Your cart will expire in 05:00 minutes", "Stock is running low",
    "Final hours - prices go up at midnight", "Only a few items left", "Book now, this price won't last",
    "Almost sold out!", "Last 2 rooms available at this price", "Flash sale ends in 2 hours",
    "Others are about to buy this - don't wait", "Today only! Free gift with every order",
    "Hurry up, this offer disappears soon", "Only 5 minutes left to claim your discount",
    "Limited quantity - order now", "Last day of the sale!", "Prices increase in 00:45:12",
    "Don't wait, someone else may take your seat", "Selling out fast, secure yours now", "This deal ends today",
    "Only 4 left - order soon", "Offer valid for the next 15 minutes only", "Act fast, limited slots remaining",
    "Last chance! Cart reserved for 3:00 minutes", "ENDS SOON: up to 70% off", "Hurry, the clock is ticking",
    "Only 2 rooms left on our site!", "Almost gone: just 1 left", "Limited-time deal ending soon",
    "You have 10 minutes to complete your order", "Last few pieces remaining",
    "Book before midnight to keep this price", "Don't let this deal slip away", "Few left! Order today",
    "Countdown: sale ends in 03:21:09", "In high demand - 3 left at this price", "Hurry, stocks are limited!",
    "Offer expires today", "Buy now before the price goes up", "Only 10 minutes remaining!",
    "Get it now, it won't be available for long",
    # added: limited stock, countdowns, last chance, booking pressure, scarcity claims
    "Only 2 items left at this price", "Hurry, this deal ends tonight", "Last chance to claim this offer",
    "Only 5 minutes remaining", "Just 3 left in your size - order before they're gone",
    "Price drops back to normal in 14:59", "Deal of the day ends in 01:12:45",
    "Rooms are filling up fast for your dates", "Don't wait - this offer won't come back",
    "Only 6 tickets left for this show", "Complete your purchase now to lock in this price",
    "Over 40 people have this in their cart right now", "Hurry! Your reserved discount expires soon",
    "Weekend sale: final few hours remaining", "Last unit in stock - buy it before it sells out",
    "Limited-time price - ends at midnight tonight", "Seats going quickly for your selected date",
    "Claim your coupon in the next 02:00 or lose it",
]

CONFIRM_SHAMING = [
    "No, I don't want to save money.", "No thanks, I prefer paying full price.",
    "No, I'd rather miss out on this deal.", "I don't want to protect my account.",
    "No, I like being overcharged.", "No thanks, I hate saving money.", "No, I don't care about my health.",
    "No, I'm happy to pay more.", "I'd rather pay more.", "No thanks, I don't want free shipping.",
    "No, I'll stay unprotected.", "No, I don't want to be a smart shopper.", "No, I enjoy wasting money.",
    "I don't want the discount.", "No, I don't want to look good.", "No thanks, I'm fine with higher prices.",
    "Maybe later, I prefer losing out on savings.", "No, I don't love my family enough to buy insurance.",
    "No, I don't want exclusive rewards.", "No thanks, I'm not interested in saving money.",
    "I'm okay with missing the best offer.", "No, I want to keep overpaying.", "No, I don't want to be healthy.",
    "No, I'll risk losing my data.", "No thanks, I don't like great deals.",
    "No, I don't want to protect my family.", "No thanks, I don't want to improve my life.",
    "No, I'd rather stay broke.", "No thanks, I prefer to miss out.", "No, I don't mind wasting my money.",
    "No, I'm fine being left behind.", "No, I don't want a better offer.", "No, I'd rather risk it.",
    "No thanks, I don't need to feel secure.", "No, I like paying extra.", "No, I don't want to be rewarded.",
    "No thanks, I enjoy missing out on bonuses.", "No, my privacy isn't important to me.",
    "No, I prefer the expensive option.", "No thanks, I'd rather not look after my skin.",
    "No, I don't want to get ahead.", "No thanks, I don't want to protect my purchase.",
    "No, I'm not into saving money.", "No, I'd rather be unprepared.", "No, I don't care about getting a deal.",
    "No, I don't want my wedding to be perfect.", "No thanks, I'll pay full price like everyone else.",
    "No, I like losing out on savings.", "No thanks, I'd rather my order be unprotected.",
    "No, I don't want to treat myself.",
    # added: guilt-inducing declines, self-deprecating wording, negative framing of the user's choice
    "No, I prefer paying full price", "No thanks, I don't want to save money",
    "No, I'll continue without the discount", "I don't want to protect my purchase",
    "No, I'd rather not get the best price", "No thanks, I'll skip the savings and pay more",
    "No, I'm not that serious about my fitness", "No thanks, I don't care about fast delivery",
    "No, I'm happy to leave my device unprotected", "No, I don't mind paying more for shipping",
    "No thanks, I'm not a fan of member-only prices", "No, I'll stick with paying more than everyone else",
    "No thanks, I don't want to be a VIP", "No, I'm fine with missing out on free gifts",
    "No, I don't care if my package gets lost", "No thanks, I don't want glowing skin",
    "No, I don't need to look after my pet's health", "No, I'm the kind of person who ignores a good deal",
]

NONE = [
    # plain declines and neutral choices
    "No thanks.", "No, cancel my order.", "I don't want to continue.", "No, go back.", "Decline",
    "Skip this step", "Maybe later", "Not now", "No, keep my current plan", "Cancel subscription",
    "Continue without offer", "No, thank you", "Skip for now", "I'd like to speak to an agent",
    "I don't want to receive emails.", "Remove from cart", "No, I don't want to receive offers by email.",
    "Skip the tutorial", "No thanks, I already have insurance.", "No, I'll buy it at the store.",
    # hard negatives: look like shaming/urgency words but are neutral
    "I don't want to save this address.", "No, I'd rather pay later.",
    "No, I don't want to protect this file with a password.", "Only available in black.",
    "Limited warranty: 1 year.", "Last updated: March 2025", "Left side pocket with zip",
    "Only 18+ may purchase this item", "Only genuine products sold here", "The sale starts on 1 November",
    "Subscription renews every month", "The warranty lasts 2 years", "Offer applies to orders above ₹999.",
    "Sale price valid for new customers", "Our store opens at 09:00", "Our customer service is open until 18:00",
    "Save my card for next time", "Protect your account with two-factor authentication.",
    "Save 10% when you subscribe", "Get 10% off your first order", "Pre-order now",
    # ordinary page text
    "Premium Wireless Headphones", "Free delivery available.", "Delivery takes 2 days.",
    "This product has good reviews.", "Buy our headphones.", "Add to cart", "Checkout", "TOTAL ₹967",
    "84% OFF", "Add ₹50 donation", "Platform fee ₹49", "Delivery ₹99", "Handling fee ₹20",
    "Estimated delivery: 12 Oct", "Free returns within 30 days.", "Contact us for bulk orders",
    "Terms and conditions apply", "In stock", "Available in 3 colours", "Battery lasts up to 30 hours",
    "Sold by Acme Retail", "Sign in to continue", "Thanks for your order!", "Order confirmed",
    "I agree to the terms", "Remember me", "Forgot password?", "Reviews (1,240)", "Shop now", "Learn more",
    "New arrivals", "Product weight: 250 g", "Customers also viewed", "This product is available.",
    # added: hard negatives with "only", "no", "save", "left", "last", "ends" used innocently
    "Save this address", "Only one size is currently available", "No additional fees apply",
    "Maximum 2 units per order", "No, I don't need a gift receipt", "No, keep my shipping address as is",
    "Cash on delivery is not available for this item", "Save for later",
    "Valid from 1 to 31 October 2026", "No, I don't want to subscribe to the newsletter",
    "No, use the standard delivery option", "Only prepaid orders are eligible for this coupon",
    "No cost EMI available on select cards", "Left earbud and right earbud included", "Save changes",
    "No, don't save my payment details", "Out of stock - notify me when available",
    "Sale items cannot be returned", "Last name",
    # added: factual hard negatives around "no", "not available", "only", "limited", "eligible",
    # "valid", "left" and "save" (policies, payments, delivery, warranty, inventory, account settings)
    "No additional warranty is included.", "No payment is required today.",
    "No delivery is available to this location.", "No returns are accepted on innerwear.",
    "No account is needed to check out as a guest.", "No, I'd like to change my delivery date.",
    "No coupon code is needed for this price.",
    "Cash on delivery is not available.", "This size is not available.",
    "Express delivery is not available for this address.", "Gift wrapping is not available for this item.",
    "Pickup is not available at this store.",
    "Only black is currently available.", "This product is available only in medium.",
    "Only digital payment methods are supported.", "The coupon is valid only for selected categories.",
    "Only registered users can write reviews.",
    "This warranty is limited to manufacturing defects.", "Returns are limited to unopened products.",
    "The storage period is limited to 30 days.", "Free shipping is limited to orders within India.",
    "Students are eligible for this discount.", "Only registered users are eligible for the offer.",
    "This coupon is available to eligible customers.", "Orders above ₹499 are eligible for free delivery.",
    "This coupon is valid until 31 October.", "The warranty is valid for one year.",
    "This offer is valid for selected products.", "Your gift card is valid for 12 months from purchase.",
    "The items left in your cart are saved for later.", "The amount left to pay is ₹799.",
    "The remaining balance left on your account is ₹200.",
    "Left-handed models are listed under Accessories.",
    "Your changes have been saved.", "Saved addresses can be edited in account settings.",
    "Save the invoice as a PDF from the order page.",
    "Inventory is updated every 24 hours.", "Orders to remote pin codes may take 2 extra days.",
    "Shipping to PO boxes is not supported.", "Items marked as final sale cannot be exchanged.",
    "Batteries are not included with this product.", "Next restock is expected in November.",
]

LABELED = {"FALSE_URGENCY": FALSE_URGENCY, "CONFIRM_SHAMING": CONFIRM_SHAMING, "NONE": NONE}
SPLITS = (("train", 0.70), ("val", 0.15), ("test", 0.15))
SEED = 42
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def build():
    rng = random.Random(SEED)
    seen, rows = {}, {"train": [], "val": [], "test": []}
    for label, texts in LABELED.items():
        unique = []
        for t in texts:
            k = _key(t)
            if k in seen:
                raise ValueError(f"Duplicate example: {t!r} (labels {seen[k]} and {label})")
            seen[k] = label
            unique.append(t)
        rng.shuffle(unique)
        n = len(unique)
        n_train, n_val = round(n * SPLITS[0][1]), round(n * SPLITS[1][1])
        rows["train"] += [(t, label) for t in unique[:n_train]]
        rows["val"] += [(t, label) for t in unique[n_train:n_train + n_val]]
        rows["test"] += [(t, label) for t in unique[n_train + n_val:]]
    for split in rows:
        rng.shuffle(rows[split])
    return rows


def write(rows):
    os.makedirs(OUT_DIR, exist_ok=True)
    everything = [r for split in ("train", "val", "test") for r in rows[split]]
    for name, data in (("train", rows["train"]), ("val", rows["val"]), ("test", rows["test"]), ("all", everything)):
        with open(os.path.join(OUT_DIR, f"{name}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["text", "label"])
            w.writerows(data)


if __name__ == "__main__":
    rows = build()
    write(rows)
    for split, data in rows.items():
        counts = {lab: sum(1 for _, l in data if l == lab) for lab in LABELED}
        print(f"{split:5} {len(data):4} samples  {counts}")