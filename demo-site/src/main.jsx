import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const PRODUCT = {
  name: 'Aster Wireless Headphones',
  price: 799,
  originalPrice: 4999,
  donation: 50,
  delivery: 99,
  platformFee: 49,
  handlingFee: 20,
};

function formatINR(value) {
  return `₹${value.toLocaleString('en-IN')}`;
}

function navigate(path) {
  window.history.pushState({}, '', path);
  window.dispatchEvent(new PopStateEvent('popstate'));
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function App() {
  const [path, setPath] = useState(window.location.pathname || '/');
  const [darkMode, setDarkMode] = useState(() => window.localStorage.getItem('morrow-theme') === 'dark');
  const [donationChecked, setDonationChecked] = useState(true);
  const [secondsLeft, setSecondsLeft] = useState(8 * 60 + 32);

  useEffect(() => {
    const onPopState = () => setPath(window.location.pathname || '/');
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = darkMode ? 'dark' : 'light';
    window.localStorage.setItem('morrow-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  useEffect(() => {
    const timer = window.setInterval(() => setSecondsLeft((value) => (value > 0 ? value - 1 : 8 * 60 + 32)), 1000);
    return () => window.clearInterval(timer);
  }, []);

  const minutes = String(Math.floor(secondsLeft / 60)).padStart(2, '0');
  const seconds = String(secondsLeft % 60).padStart(2, '0');
  const total = PRODUCT.price + PRODUCT.delivery + PRODUCT.platformFee + PRODUCT.handlingFee + (donationChecked ? PRODUCT.donation : 0);

  const page = useMemo(() => {
    if (path === '/product') return <ProductPage minutes={minutes} seconds={seconds} />;
    if (path === '/cart') return <CartPage />;
    if (path === '/checkout') return <CheckoutPage donationChecked={donationChecked} setDonationChecked={setDonationChecked} total={total} />;
    if (path === '/subscribe') return <SubscribePage />;
    if (path === '/cancel') return <CancelPage />;
    if (path === '/bait-switch') return <BaitSwitchPage />;
    if (path === '/interface-interference') return <InterfaceInterferencePage />;
    if (path === '/clean-page') return <CleanPage />;
    return <HomePage />;
  }, [path, minutes, seconds, donationChecked, total]);

  return <div className="store-shell">
    <div className="store-notice"><span>Complimentary delivery on orders over ₹1,500</span><button onClick={() => navigate('/subscribe')}>Join Morrow Circle →</button></div>
    <header className="store-header">
      <button className="store-brand" onClick={() => navigate('/')} aria-label="Go to Morrow Market home"><span className="store-mark">M</span><span>Morrow Market</span></button>
      <nav className="store-nav" aria-label="Store navigation"><button onClick={() => navigate('/')}>Home</button><button onClick={() => navigate('/product')}>Shop</button><button onClick={() => navigate('/subscribe')}>Morrow Circle</button><button onClick={() => navigate('/cart')}>Cart <span className="cart-count">1</span></button><button className="store-theme" onClick={() => setDarkMode((value) => !value)} aria-label="Toggle store theme">{darkMode ? '☀' : '☾'}</button></nav>
    </header>
    <main>{page}</main>
    <footer className="store-footer"><div><strong>Morrow Market</strong><span>Objects for the everyday, chosen with care.</span></div><div><span>Shipping & returns</span><span>Customer care</span><span>Demo store · No real payment</span></div></footer>
  </div>;
}

function HomePage() {
  return <div className="store-page home-page">
    <section className="store-hero"><div className="hero-copy"><span className="store-kicker">THE AUTUMN EDIT · 2026</span><h1>Good things for the way you live.</h1><p>Thoughtful audio, useful objects, and small upgrades that make everyday spaces feel like your own.</p><div className="hero-actions"><button className="store-primary" onClick={() => navigate('/product')}>Shop the edit <span>→</span></button><button className="store-secondary" onClick={() => navigate('/subscribe')}>Explore membership</button></div></div><div className="hero-product"><div className="hero-circle" /><img src="/assets/headphones-product.jpg" alt="Aster wireless headphones" /><span>01 / 04</span></div></section>
    <section className="category-row"><button onClick={() => navigate('/product')}><span>Audio</span><small>12 objects</small></button><button onClick={() => navigate('/product')}><span>Desk</span><small>08 objects</small></button><button onClick={() => navigate('/product')}><span>Travel</span><small>16 objects</small></button><button onClick={() => navigate('/product')}><span>Gifting</span><small>Curated sets</small></button></section>
    <section className="section-block"><div className="section-title"><div><span className="store-kicker">OUR CURRENT FAVORITES</span><h2>Made to be lived with.</h2></div><button className="inline-link" onClick={() => navigate('/product')}>View all pieces →</button></div><div className="product-grid"><ProductTile image="/assets/headphones-product.jpg" label="Audio" title="Aster Wireless Headphones" price="₹799" meta="Midnight / Studio series" /><ProductTile label="Desk" title="Arc Task Light" price="₹1,499" meta="Sand / Soft glow" visual="lamp" /><ProductTile label="Travel" title="Fold Weekender" price="₹2,299" meta="Olive / 38L" visual="bag" /></div></section>
    <section className="story-banner"><div><span className="store-kicker">THE MORROW STANDARD</span><h2>Less noise. More keepers.</h2><p>We look for considered materials, useful details, and objects that earn their place.</p></div><button className="store-secondary" onClick={() => navigate('/product')}>Read our approach</button></section>
  </div>;
}

function ProductTile({ image, label, title, price, meta, visual }) {
  const visualAsset = visual === 'lamp' ? '/assets/arc-task-light.jpg' : visual === 'bag' ? '/assets/fold-weekender.jpg' : image;
  return <article className="product-tile" onClick={() => navigate('/product')}><div className={`tile-visual ${visual || ''}`}>{visualAsset ? <img src={visualAsset} alt={`${title} product photo`} /> : null}<small>{label}</small></div><div className="tile-info"><div><h3>{title}</h3><p>{meta}</p></div><strong>{price}</strong></div></article>;
}

function ProductPage({ minutes, seconds }) {
  return <div className="store-page product-page"><div className="store-breadcrumb">Home <span>/</span> Audio <span>/</span> Headphones</div><section className="product-detail"><div className="product-photo"><img src="/assets/headphones-product.jpg" alt="Black Aster wireless headphones" /><span>ASTER / STUDIO SERIES</span></div><div className="product-info"><span className="store-kicker">ASTER · STUDIO SERIES</span><h1>{PRODUCT.name}</h1><p className="product-rating">★★★★★ <span>4.9 · 2,481 reviews</span></p><div className="product-price"><strong>{formatINR(PRODUCT.price)}</strong><del>{formatINR(PRODUCT.originalPrice)}</del><span>84% off</span></div><p className="product-description">Immersive sound, adaptive noise control, and a quiet confidence that travels well.</p><div className="stock-panel" data-ccpa-pattern="FALSE_URGENCY"><div><strong id="scarcity-text">ONLY 2 LEFT!</strong><span> in stock</span></div><div><span>Offer reserved for</span><strong id="offer-timer">{minutes}:{seconds}</strong></div></div><div className="feature-row"><span>48-hour battery</span><span>Adaptive ANC</span><span>Free travel case</span></div><button className="store-primary full-button" onClick={() => navigate('/cart')}>Add to cart <span>→</span></button><button className="wishlist">♡ Add to wishlist</button><div className="delivery-note"><strong>Free delivery on orders over ₹1,500</strong><span>Ships in 2–4 business days · 30-day returns</span></div></div></section><section className="detail-tabs"><button className="selected">Details</button><button>Materials</button><button>Shipping & returns</button></section><section className="detail-copy"><h2>Designed for the long listen.</h2><p>Aster balances warm low-end detail with clear vocals and a comfortable fit for the commute, the studio, and the slow Sunday morning.</p></section></div>;
}

function CartPage() {
  return <div className="store-page narrow-page"><div className="store-breadcrumb">Home <span>/</span> Cart</div><div className="page-heading"><div><span className="store-kicker">YOUR BAG</span><h1>One good choice.</h1></div><span className="item-count">1 item</span></div><section className="cart-layout"><div className="cart-item"><div className="cart-image"><img src="/assets/headphones-product.jpg" alt="Aster headphones" /></div><div><h2>{PRODUCT.name}</h2><p>Midnight graphite · 1 unit</p><button className="remove-link">Remove</button></div><strong>{formatINR(PRODUCT.price)}</strong></div><aside className="summary-card"><span className="store-kicker">SUMMARY</span><div><span>Subtotal</span><strong>{formatINR(PRODUCT.price)}</strong></div><div><span>Delivery</span><small>Calculated at checkout</small></div><button className="store-primary full-button" onClick={() => navigate('/checkout')}>Continue to checkout <span>→</span></button><p>Demo store · no payment will be taken</p></aside></section></div>;
}

function CheckoutPage({ donationChecked, setDonationChecked, total }) {
  return <div className="store-page narrow-page"><div className="store-breadcrumb">Home <span>/</span> Cart <span>/</span> Checkout</div><div className="page-heading"><div><span className="store-kicker">ALMOST YOURS</span><h1>Checkout</h1></div><span className="secure-pill">Secure checkout</span></div><section className="checkout-layout"><div className="checkout-main"><section className="checkout-card"><h2>Delivery details</h2><div className="field-grid"><label>First name<input placeholder="Alex" /></label><label>Last name<input placeholder="Morgan" /></label><label className="wide">Address<input placeholder="221B Baker Street" /></label><label>City<input placeholder="Mumbai" /></label><label>PIN code<input placeholder="400001" /></label></div></section><section className="checkout-card" data-ccpa-pattern="BASKET_SNEAKING"><h2>Order options</h2><label className="option-row" htmlFor="donation"><input id="donation" type="checkbox" checked={donationChecked} onChange={(event) => setDonationChecked(event.target.checked)} /><span className="custom-check" /><span><strong>Add ₹50 to support responsible packaging</strong><small>A small contribution helps us reduce single-use materials.</small></span><strong>{formatINR(PRODUCT.donation)}</strong></label><div className="choice-row"><span>Want to skip this?</span><button id="confirm-shaming" type="button" onClick={() => setDonationChecked(false)}>No, I don't want to save money.</button></div></section><section className="checkout-card"><h2>Payment</h2><div className="payment-box"><span>▣</span><div><strong>Card ending in 4242</strong><small>Encrypted and protected</small></div><span>✓</span></div></section></div><aside className="summary-card sticky-summary" data-ccpa-pattern="DRIP_PRICING"><span className="store-kicker">ORDER SUMMARY</span><div className="summary-product"><span>{PRODUCT.name}<small>1 unit</small></span><strong>{formatINR(PRODUCT.price)}</strong></div><hr /><div className="drip-tag"><span>Delivery</span><strong>{formatINR(PRODUCT.delivery)}</strong></div><div><span>Platform fee</span><strong>{formatINR(PRODUCT.platformFee)}</strong></div><div><span>Handling fee</span><strong>{formatINR(PRODUCT.handlingFee)}</strong></div>{donationChecked && <div className="added-line"><span>Packaging contribution</span><strong>{formatINR(PRODUCT.donation)}</strong></div>}<hr /><div className="total-row"><span>Total</span><strong id="total-price">{formatINR(total)}</strong></div><button className="store-primary full-button" onClick={() => window.alert('Demo only: no order was placed.')}>Place demo order <span>→</span></button><small className="summary-note">By continuing, you agree to our terms.</small></aside></section></div>;
}

function SubscribePage() {
  return <div className="store-page narrow-page membership-page"><div className="store-breadcrumb">Home <span>/</span> Morrow Circle</div><section className="membership-hero"><span className="store-kicker">MORROW CIRCLE</span><h1>More of what you love, delivered.</h1><p>Members receive early access, private edits, and free delivery on every order.</p><div className="membership-price"><strong>₹99</strong><span>/ month</span></div><label className="option-row renewal-option" data-ccpa-pattern="SUBSCRIPTION_TRAP"><input type="checkbox" defaultChecked /><span className="custom-check" /><span><strong>Start my free 30-day trial</strong><small>Your membership renews monthly after the trial.</small></span></label><button className="store-primary" onClick={() => window.alert('Demo only: no subscription was started.')}>Start free trial <span>→</span></button><p className="fine-print">You can manage your membership from your account.</p></section><section className="membership-benefits"><div><strong>Early access</strong><span>See new collections before everyone else.</span></div><div><strong>Free delivery</strong><span>Every order, every month.</span></div><div><strong>Member edits</strong><span>Curated recommendations for your space.</span></div></section></div>;
}

function CancelPage() {
  return <div className="store-page narrow-page"><div className="store-breadcrumb">Account <span>/</span> Morrow Circle</div><section className="account-card cancel-card"><span className="store-kicker">MEMBERSHIP SETTINGS</span><h1>Manage Morrow Circle</h1><p>Your membership is active and renews on 18 November 2026.</p><div className="account-actions"><button className="store-primary">Keep membership</button><button className="quiet-button">Update payment</button><button className="quiet-button">View benefits</button></div><div className="cancel-flow"><strong>Need to cancel?</strong><div className="cancel-step">1. Review your membership benefits</div><div className="cancel-step">2. Tell us what we could improve</div><div className="cancel-step">3. Confirm cancellation</div><button className="cancel-link">Continue to cancellation</button></div></section></div>;
}

function BaitSwitchPage() {
  return <div className="store-page narrow-page"><div className="store-breadcrumb">Home <span>/</span> Audio</div><section className="comparison-page"><span className="store-kicker">CHOOSE YOUR FINISH</span><h1>Make it yours.</h1><p>Select a finish for the Aster Wireless Headphones.</p><div className="switch-options"><div className="switch-row"><span className="swatch black" /><div><strong>Midnight graphite</strong><small>{formatINR(799)} · In stock</small></div><button className="store-primary">Choose</button></div><div className="switch-row"><span className="swatch sand" /><div><strong>Warm sand</strong><small>{formatINR(799)} · In stock</small></div><button className="store-secondary">Choose</button></div></div><div id="bait-switch-status" data-ccpa-pattern="BAIT_AND_SWITCH" className="switch-status">Selected finish is reserved for 10 minutes.</div></section></div>;
}

function InterfaceInterferencePage() {
  return <div className="store-page narrow-page"><div className="store-breadcrumb">Home <span>/</span> Morrow Circle</div><section className="comparison-page"><span className="store-kicker">MEMBERSHIP PLANS</span><h1>Choose what fits.</h1><p>Flexible access to the Morrow edit.</p><div className="plan-choice preferred" data-ccpa-pattern="INTERFACE_INTERFERENCE"><span className="plan-badge">MOST POPULAR</span><h2>Circle Plus</h2><p>Free delivery, early access, and private edits.</p><strong>₹99 <small>/ month</small></strong><button className="store-primary">Choose Circle Plus</button></div><div className="plan-choice muted-choice"><h2>Shop as you go</h2><p>Pay standard delivery on each order.</p><button className="muted-link">Continue without membership</button></div></section></div>;
}

function CleanPage() {
  return <div className="store-page narrow-page clean-page"><div className="store-breadcrumb">Home <span>/</span> Transparency</div><section className="account-card"><span className="store-kicker">OUR PROMISE</span><h1>A clear, considered checkout.</h1><p>This control page uses transparent stock, complete pricing, neutral choices, and an equal presentation of options.</p><div className="clean-list"><div><strong>12 units available</strong><span>No artificial countdown or scarcity message.</span></div><div><strong>Optional extras start unchecked</strong><span>You choose before anything is added.</span></div><div><strong>Complete price shown early</strong><span>Fees are visible before checkout.</span></div></div><button className="store-secondary" onClick={() => navigate('/product')}>Continue shopping</button></section></div>;
}

createRoot(document.getElementById('root')).render(<App />);
