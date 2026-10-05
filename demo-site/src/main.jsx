import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const PRODUCT = {
  name: 'Premium Wireless Headphones',
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
  const [donationChecked, setDonationChecked] = useState(true);
  const [secondsLeft, setSecondsLeft] = useState(8 * 60 + 32);

  useEffect(() => {
    const onPopState = () => setPath(window.location.pathname || '/');
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setSecondsLeft((value) => (value > 0 ? value - 1 : 8 * 60 + 32));
    }, 1000);
    return () => window.clearInterval(timer);
  }, []);

  const minutes = String(Math.floor(secondsLeft / 60)).padStart(2, '0');
  const seconds = String(secondsLeft % 60).padStart(2, '0');
  const subtotal = PRODUCT.price + PRODUCT.delivery + PRODUCT.platformFee + PRODUCT.handlingFee;
  const total = subtotal + (donationChecked ? PRODUCT.donation : 0);

  const page = useMemo(() => {
    if (path === '/product' || path === '/') {
      return <ProductPage minutes={minutes} seconds={seconds} />;
    }
    if (path === '/cart') {
      return <CartPage />;
    }
    if (path === '/checkout') {
      return (
        <CheckoutPage
          donationChecked={donationChecked}
          setDonationChecked={setDonationChecked}
          total={total}
        />
      );
    }
    return <ProductPage minutes={minutes} seconds={seconds} />;
  }, [path, minutes, seconds, donationChecked, total]);

  return (
    <div className="app-shell">
      <header className="site-header">
        <button className="brand" onClick={() => navigate('/')} aria-label="Go to DarkShop home">
          <span className="brand-mark">DS</span>
          <span>DarkShop</span>
        </button>
        <nav className="main-nav" aria-label="Primary navigation">
          <button onClick={() => navigate('/product')}>Shop</button>
          <button onClick={() => navigate('/cart')}>Cart <span className="cart-count">1</span></button>
        </nav>
      </header>
      <main>{page}</main>
      <footer className="site-footer">
        <span>DarkShop demo environment</span>
        <span>Secure checkout · 30-day returns</span>
      </footer>
    </div>
  );
}

function ProductPage({ minutes, seconds }) {
  return (
    <div className="page-wrap">
      <div className="breadcrumb">Home <span>/</span> Audio <span>/</span> Headphones</div>
      <section className="product-layout" id="product-page" data-page="product">
        <div className="product-visual">
          <div className="product-glow" />
          <div className="headphone-art" aria-label="Wireless headphones product illustration">
            <div className="headband" />
            <div className="earcup left" />
            <div className="earcup right" />
          </div>
          <div className="visual-caption">STUDIO SERIES / 2025</div>
        </div>
        <div className="product-copy">
          <div className="eyebrow">LIMITED DROP · #DS-440</div>
          <h1>Premium Wireless Headphones</h1>
          <p className="rating">★★★★★ <span>4.9 · 2,481 reviews</span></p>
          <div className="price-row">
            <span id="current-price" className="current-price">{formatINR(PRODUCT.price)}</span>
            <span id="original-price" className="original-price">{formatINR(PRODUCT.originalPrice)}</span>
            <span id="discount-label" className="discount-label">84% OFF</span>
          </div>
          <p className="price-note">Today only: studio-quality sound at a launch-week price.</p>

          <div className="urgency-panel" aria-label="Limited time offer">
            <div className="urgency-line"><span className="flame">◆</span><strong id="scarcity-text">ONLY 2 LEFT!</strong><span>in stock</span></div>
            <div className="timer-line"><span>Offer reserved for</span><strong id="offer-timer">{minutes}:{seconds}</strong></div>
          </div>

          <div className="feature-list">
            <span>48-hour battery</span><span>Adaptive ANC</span><span>Free case included</span>
          </div>
          <button id="buy-now" className="primary-cta" onClick={() => navigate('/cart')}>BUY NOW <span>→</span></button>
          <button className="text-link" onClick={() => navigate('/cart')}>Add to wishlist</button>
        </div>
      </section>
      <section className="trust-strip">
        <div><strong>Fast delivery</strong><span>Arrives in 2–4 days</span></div>
        <div><strong>Easy returns</strong><span>30-day return promise</span></div>
        <div><strong>Protected payment</strong><span>Encrypted checkout</span></div>
      </section>
    </div>
  );
}

function CartPage() {
  return (
    <div className="page-wrap narrow" data-page="cart">
      <div className="breadcrumb">Home <span>/</span> Cart</div>
      <div className="page-heading"><div><div className="eyebrow">YOUR SELECTION</div><h1>Your cart</h1></div><span className="cart-status">1 item</span></div>
      <section className="cart-card">
        <div className="cart-product">
          <div className="mini-headphones"><div className="mini-band" /><div className="mini-cup left" /><div className="mini-cup right" /></div>
          <div><strong>{PRODUCT.name}</strong><span>Midnight graphite · 1 unit</span></div>
          <strong id="cart-price">{formatINR(PRODUCT.price)}</strong>
        </div>
        <div className="cart-summary">
          <div><span>Subtotal</span><strong>{formatINR(PRODUCT.price)}</strong></div>
          <div><span>Delivery</span><span className="muted">Calculated at checkout</span></div>
          <button className="primary-cta" onClick={() => navigate('/checkout')}>CONTINUE TO CHECKOUT <span>→</span></button>
        </div>
      </section>
      <div className="cart-note"><span className="note-icon">i</span> You are one step away from completing your order.</div>
    </div>
  );
}

function CheckoutPage({ donationChecked, setDonationChecked, total }) {
  return (
    <div className="page-wrap narrow" data-page="checkout">
      <div className="breadcrumb">Home <span>/</span> Cart <span>/</span> Checkout</div>
      <div className="page-heading"><div><div className="eyebrow">ALMOST YOURS</div><h1>Checkout</h1></div><span className="secure-badge">● Secure</span></div>
      <div className="checkout-grid">
        <section className="checkout-main">
          <div className="section-card">
            <div className="section-title"><span className="step-dot">1</span><div><h2>Delivery details</h2><p>Where should we send your order?</p></div></div>
            <div className="field-grid"><label>First name<input placeholder="Alex" /></label><label>Last name<input placeholder="Morgan" /></label><label className="wide">Address<input placeholder="221B Baker Street" /></label><label>City<input placeholder="Mumbai" /></label><label>PIN code<input placeholder="400001" /></label></div>
          </div>
          <div className="section-card">
            <div className="section-title"><span className="step-dot">2</span><div><h2>Order options</h2><p>Personalize your delivery</p></div></div>
            <label className="option-row" htmlFor="donation">
              <input id="donation" data-testid="donation-checkbox" type="checkbox" checked={donationChecked} onChange={(event) => setDonationChecked(event.target.checked)} />
              <span className="checkmark" />
              <span className="option-copy"><strong>Add ₹50 donation</strong><small>Support responsible packaging for this order.</small></span>
              <strong>{formatINR(PRODUCT.donation)}</strong>
            </label>
            <div className="shaming-box"><span>Not interested?</span><button id="confirm-shaming" type="button" onClick={() => setDonationChecked(false)}>No, I don't want to save money.</button></div>
          </div>
          <div className="section-card">
            <div className="section-title"><span className="step-dot">3</span><div><h2>Payment</h2><p>Demo mode — no payment will be taken</p></div></div>
            <div className="payment-placeholder"><span>▣</span><div><strong>Card ending in 4242</strong><small>Encrypted and protected</small></div><span>✓</span></div>
          </div>
        </section>
        <aside className="order-card">
          <div className="eyebrow">ORDER SUMMARY</div>
          <div className="order-line product-line"><span>{PRODUCT.name}<small>1 unit</small></span><strong>{formatINR(PRODUCT.price)}</strong></div>
          <div className="rule" />
          <div className="order-line"><span>Delivery</span><strong>{formatINR(PRODUCT.delivery)}</strong></div>
          <div className="order-line"><span>Platform fee</span><strong>{formatINR(PRODUCT.platformFee)}</strong></div>
          <div className="order-line"><span>Handling fee</span><strong>{formatINR(PRODUCT.handlingFee)}</strong></div>
          {donationChecked && <div className="order-line added-line"><span>Donation add-on</span><strong>{formatINR(PRODUCT.donation)}</strong></div>}
          <div className="rule" />
          <div className="total-line"><span>TOTAL</span><strong id="total-price">{formatINR(total)}</strong></div>
          <button id="place-order" className="primary-cta" type="button" onClick={() => window.alert('Demo only: no order was placed.')}>PLACE DEMO ORDER <span>→</span></button>
          <p className="order-footnote">By continuing, you agree to our demo terms.</p>
        </aside>
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
