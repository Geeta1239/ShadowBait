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

const CCPA_PATTERNS = [
  ['01', 'False Urgency', 'VERIFIED', 'Scarcity and a countdown push immediate action.'],
  ['02', 'Basket Sneaking', 'VERIFIED', 'An optional donation starts selected.'],
  ['03', 'Confirm Shaming', 'VERIFIED', 'The decline option uses guilt-oriented language.'],
  ['04', 'Forced Action', 'SIMULATED', 'A sample purchase flow asks for an unrelated email opt-in.'],
  ['05', 'Subscription Trap', 'VERIFIED', 'A free trial is easy to start but cancellation is hard to find.'],
  ['06', 'Interface Interference', 'VERIFIED', 'A preferred action is highlighted while the alternative is muted.'],
  ['07', 'Bait and Switch', 'VERIFIED', 'A low-price product becomes unavailable at the final step.'],
  ['08', 'Drip Pricing', 'VERIFIED', 'Fees appear later in checkout and require price-flow review.'],
  ['09', 'Disguised Advertisement', 'SIMULATED', 'Sponsored content is styled like an independent review.'],
  ['10', 'Nagging', 'SIMULATED', 'Repeated prompts ask the user to install an app or subscribe.'],
  ['11', 'Trick Question', 'SIMULATED', 'A confusing choice uses ambiguous or double-negative wording.'],
  ['12', 'SaaS Billing', 'SIMULATED', 'A free trial silently rolls into recurring billing.'],
  ['13', 'Rogue Malware', 'EXCLUDED', 'Not implemented: no malware-like behavior is created in this demo.'],
];


const CCPA_DIFFS = [
  { id: '01', rule: 'False Urgency', status: 'VERIFIED', evidence: '“ONLY 2 LEFT!” + resetting countdown', harm: 'Pressures people to buy before they can compare options or verify the claim.', ethical: 'Show truthful stock and a fixed, clearly stated offer end time.', route: '/product' },
  { id: '02', rule: 'Basket Sneaking', status: 'VERIFIED', evidence: 'Optional ₹50 donation is pre-selected', harm: 'Raises the payable amount without an explicit affirmative choice.', ethical: 'Start optional add-ons unchecked and explain them plainly.', route: '/checkout' },
  { id: '03', rule: 'Confirm Shaming', status: 'VERIFIED', evidence: '“No, I don’t want to save money.”', harm: 'Uses guilt to steer a consumer into an optional transaction.', ethical: 'Use neutral choices: “Add donation” / “Continue without donation.”', route: '/checkout' },
  { id: '04', rule: 'Forced Action', status: 'SIMULATED', evidence: 'Unrelated email opt-in is requested during purchase', harm: 'Makes access to the wanted product conditional on an unrelated action.', ethical: 'Keep unrelated consent optional and separate from purchase.', route: '/ccpa-lab' },
  { id: '05', rule: 'Subscription Trap', status: 'VERIFIED', evidence: 'Free trial is easy; cancellation takes multiple steps', harm: 'Makes it harder to stop recurring charges than to start them.', ethical: 'Offer cancellation with the same visibility and simplicity as sign-up.', route: '/subscribe' },
  { id: '06', rule: 'Interface Interference', status: 'VERIFIED', evidence: 'Recommended plan is prominent; basic option is visually muted', harm: 'Obscures the consumer’s lower-commitment choice through visual hierarchy.', ethical: 'Give both consequential choices equal prominence and clarity.', route: '/interface-interference' },
  { id: '07', rule: 'Bait and Switch', status: 'VERIFIED', evidence: '₹799 item becomes unavailable at final step', harm: 'Wastes time and redirects purchase intent toward a more expensive item.', ethical: 'Keep the advertised outcome available or disclose changes immediately.', route: '/bait-switch' },
  { id: '08', rule: 'Drip Pricing', status: 'VERIFIED', evidence: 'Delivery, platform, and handling fees appear after the product price', harm: 'Prevents an accurate price comparison until late in the journey.', ethical: 'Show the complete payable estimate beside the product price.', route: '/checkout' },
  { id: '09', rule: 'Disguised Advertisement', status: 'SIMULATED', evidence: 'Sponsored content resembles an independent review', harm: 'Reduces the consumer’s ability to recognize commercial persuasion.', ethical: 'Label sponsored content clearly before the consumer engages.', route: '/ccpa-lab' },
  { id: '10', rule: 'Nagging', status: 'SIMULATED', evidence: 'Repeated app or subscription prompts', harm: 'Interrupts the user until fatigue changes the decision.', ethical: 'Respect dismissal and do not repeat a declined prompt in the same session.', route: '/ccpa-lab' },
  { id: '11', rule: 'Trick Question', status: 'SIMULATED', evidence: 'Ambiguous or double-negative choices', harm: 'Increases accidental consent by making the intended outcome unclear.', ethical: 'Use short, direct labels that describe the result of each action.', route: '/ccpa-lab' },
  { id: '12', rule: 'SaaS Billing', status: 'SIMULATED', evidence: 'Trial rolls into recurring billing without a clear reminder', harm: 'Creates unexpected recurring charges after the consumer’s original intent ends.', ethical: 'Give prominent renewal notice and require clear affirmative consent.', route: '/subscribe' },
  { id: '13', rule: 'Rogue Malware', status: 'EXCLUDED', evidence: 'Not implemented in this safe demo', harm: 'Malware-like deception could compromise devices and personal data.', ethical: 'Never create fake virus warnings or malicious downloads.', route: '/ccpa-lab' },
];


const INSPECTION_FINDINGS = [
  { id: 'DP01', name: 'False Urgency', route: '/product', selector: '#scarcity-text + #offer-timer', image: '/assets/inspection/dp01-false-urgency-product.png', evidence: '“ONLY 2 LEFT!” appears beside a countdown timer.', why: 'Captured to prove scarcity text and a time-pressure signal are visible together.', harm: 'Pressures customers to buy before comparing options or verifying the claim.' },
  { id: 'DP02', name: 'Basket Sneaking', route: '/checkout', selector: '#donation', image: '/assets/inspection/dp02-dp03-dp08-checkout-before.png', evidence: 'Optional ₹50 donation checkbox starts checked.', why: 'Captured before interaction to preserve the original checked state.', harm: 'Adds an optional charge without an explicit affirmative choice.' },
  { id: 'DP03', name: 'Confirm Shaming', route: '/checkout', selector: '#confirm-shaming', image: '/assets/inspection/dp02-dp03-dp08-checkout-before.png', evidence: '“No, I don’t want to save money.”', why: 'Captured because the decline wording itself is the evidence.', harm: 'Uses guilt to steer customers toward an optional transaction.' },
  { id: 'DP05', name: 'Subscription Trap', route: '/subscribe', selector: '[data-ccpa-pattern="SUBSCRIPTION_TRAP"]', image: '/assets/inspection/dp05-subscription-trap-start.png', evidence: 'Automatic renewal is selected and cancellation is routed elsewhere.', why: 'Captured to compare the easy signup path with the separate cancellation flow.', harm: 'Makes recurring billing easier to start than to stop.' },
  { id: 'DP06', name: 'Interface Interference', route: '/interface-interference', selector: '[data-ccpa-pattern="INTERFACE_INTERFERENCE"]', image: '/assets/inspection/dp06-interface-interference.png', evidence: 'Recommended plan is prominent while Basic is visually muted.', why: 'Captured to compare the visual hierarchy of the two consequential choices.', harm: 'Obscures the customer’s lower-commitment choice.' },
  { id: 'DP07', name: 'Bait and Switch', route: '/bait-switch', selector: '#bait-switch-status', image: '/assets/inspection/dp07-bait-and-switch.png', evidence: '₹799 selection becomes an unavailable ₹1,999 upgrade at the final step.', why: 'Captured to preserve both the selected offer and the changed final outcome.', harm: 'Wastes time and redirects purchase intent toward a more expensive item.' },
  { id: 'DP08', name: 'Drip Pricing', route: '/checkout', selector: '[data-ccpa-pattern="DRIP_PRICING"]', image: '/assets/inspection/dp02-dp03-dp08-checkout-before.png', evidence: 'Delivery, platform, and handling fees appear in the later checkout summary.', why: 'Captured to show the product price beside the later fee breakdown and total.', harm: 'Delays accurate price comparison until late in the journey.' },
];

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
  const [darkMode, setDarkMode] = useState(() => window.localStorage.getItem('shadowbait-theme') === 'dark');
  const [donationChecked, setDonationChecked] = useState(true);
  const [secondsLeft, setSecondsLeft] = useState(8 * 60 + 32);
  const resetTestState = () => { setDonationChecked(true); setSecondsLeft(8 * 60 + 32); setDarkMode(false); navigate('/product'); };

  useEffect(() => {
    const onPopState = () => setPath(window.location.pathname || '/');
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = darkMode ? 'dark' : 'light';
    window.localStorage.setItem('shadowbait-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  useEffect(() => {
    const timer = window.setInterval(() => setSecondsLeft((value) => (value > 0 ? value - 1 : 8 * 60 + 32)), 1000);
    return () => window.clearInterval(timer);
  }, []);

  const minutes = String(Math.floor(secondsLeft / 60)).padStart(2, '0');
  const seconds = String(secondsLeft % 60).padStart(2, '0');
  const total = PRODUCT.price + PRODUCT.delivery + PRODUCT.platformFee + PRODUCT.handlingFee + (donationChecked ? PRODUCT.donation : 0);

  const page = useMemo(() => {
    if (path === '/ccpa-lab') return <PatternLabPage />;
    if (path === '/diff') return <DiffPage />;
    if (path === '/inspect') return <InspectionPage />;
    if (path === '/clean-page') return <CleanComparisonPage />;
    if (path === '/subscribe') return <SubscribePage />;
    if (path === '/cancel') return <CancelPage />;
    if (path === '/bait-switch') return <BaitSwitchPage />;
    if (path === '/interface-interference') return <InterfaceInterferencePage />;
    if (path === '/cart') return <CartPage />;
    if (path === '/checkout') return <CheckoutPage donationChecked={donationChecked} setDonationChecked={setDonationChecked} total={total} />;
    return <ProductPage minutes={minutes} seconds={seconds} />;
  }, [path, minutes, seconds, donationChecked, total]);

  return (
    <div className="app-shell">
      <div className="demo-ribbon"><strong>CCPA PATTERN LAB</strong><span>Controlled demo • patterns are simulated for scanner testing</span></div>
      <header className="site-header">
        <button className="brand" onClick={() => navigate('/')} aria-label="Go to DarkShop home"><span className="brand-mark">DS</span><span>DarkShop</span></button>
        <nav className="main-nav" aria-label="Primary navigation">
          <button onClick={() => navigate('/product')}>Shop</button>
          <button className="lab-link" onClick={() => navigate('/ccpa-lab')}>CCPA Lab <span className="lab-count">12</span></button><button className="diff-link" onClick={() => navigate('/diff')}>Interactive Diff</button><button className="inspect-link" onClick={() => navigate('/inspect')}>Start Inspection</button><button className="reset-link" data-testid="reset-test-state" onClick={resetTestState}>Reset Test State</button><button className="theme-toggle" onClick={() => setDarkMode((value) => !value)} aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'} title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}><span aria-hidden="true">{darkMode ? '☀' : '☾'}</span><small>{darkMode ? 'Light' : 'Dark'}</small></button>
          <button onClick={() => navigate('/cart')}>Cart <span className="cart-count">1</span></button>
        </nav>
      </header>
      <main>{page}</main>
      <footer className="site-footer"><span>DarkShop controlled research environment</span><span>Not legal advice · No real payment or malware</span></footer>
    </div>
  );
}



function CleanComparisonPage() {
  return <div className="page-wrap clean-page"><div className="breadcrumb">Home <span>/</span> Test Controls <span>/</span> Clean Comparison</div><div className="clean-hero"><div><div className="eyebrow">CONTROL · FALSE-POSITIVE TEST</div><h1>Clean ethical shopping page</h1><p>This page intentionally contains normal, transparent UI. The scanner should produce zero verified dark-pattern findings here.</p></div><span className="clean-badge">EXPECTED: 0 FINDINGS</span></div><section className="clean-grid"><article className="clean-card"><span className="clean-icon">✓</span><div><h2>Transparent offer</h2><p>Stock is shown truthfully: 12 units available. No countdown or fake scarcity.</p></div></article><article className="clean-card"><span className="clean-icon">✓</span><div><h2>Neutral options</h2><p>Optional add-ons start unchecked and the decline action uses neutral wording.</p></div></article><article className="clean-card"><span className="clean-icon">✓</span><div><h2>Complete price</h2><p>Product, delivery, platform, and handling fees are disclosed before checkout.</p></div></article><article className="clean-card"><span className="clean-icon">✓</span><div><h2>Equal choices</h2><p>Continue and choose-basic options use equal contrast, size, and clear labels.</p></div></article></section><div className="clean-actions"><button className="primary-cta" data-testid="clean-page-pass" onClick={() => navigate('/inspect')}>OPEN INSPECTION DEMO <span>→</span></button><button className="secondary-cta" onClick={() => navigate('/product')}>BACK TO DARKSHOP</button></div></div>;
}

function InspectionPage() {
  const [running, setRunning] = useState(false);
  const [completed, setCompleted] = useState(0);
  const [liveFindings, setLiveFindings] = useState([]);
  const [liveMessage, setLiveMessage] = useState('');
  const [apiError, setApiError] = useState('');
  const [scanMeta, setScanMeta] = useState(null);
  const [savedReport, setSavedReport] = useState('');
  const eventSourceRef = React.useRef(null);
  useEffect(() => () => eventSourceRef.current?.close(), []);

  const startInspection = () => {
    eventSourceRef.current?.close();
    setCompleted(0); setLiveFindings([]); setApiError(''); setSavedReport(''); setScanMeta(null);
    setLiveMessage('Connecting to the live Playwright inspection API…'); setRunning(true);
    const configuredApi = window.localStorage.getItem('shadowbait-inspection-api');
    const endpoint = configuredApi ? `${configuredApi}/api/inspection/stream` : '/api/inspection/stream';
    const target = window.location.origin;
    const source = new EventSource(`${endpoint}?target=${encodeURIComponent(target)}`);
    eventSourceRef.current = source;
    source.addEventListener('started', (event) => { const data = JSON.parse(event.data); setScanMeta(data); setLiveMessage(data.message); });
    source.addEventListener('stage', (event) => { const data = JSON.parse(event.data); setCompleted(data.completed); setLiveMessage(data.message); });
    source.addEventListener('finding', (event) => { const data = JSON.parse(event.data); setCompleted(data.completed); setLiveFindings((items) => [...items, data.finding]); setLiveMessage(data.message); });
    source.addEventListener('classification', (event) => {
      const data = JSON.parse(event.data);
      setLiveFindings((items) => items.map((item) => item.id === data.pattern_id ? { ...item, m2_status: data.status, m2_findings: data.findings || [] } : item));
      setLiveMessage(data.message);
    });
    source.addEventListener('complete', (event) => { const data = JSON.parse(event.data); setCompleted(data.completed); setLiveFindings(data.findings || []); setSavedReport(data.report_file || ''); setScanMeta((meta) => ({ ...meta, finished_at: data.finished_at, summary: data.summary })); setLiveMessage(data.message); setRunning(false); source.close(); });
    source.addEventListener('error', (event) => { let message = 'Live inspection API could not be reached.'; try { message = JSON.parse(event.data).message; } catch {} setApiError(`${message} Start backend/inspection_server.py on port 5050, then reload the page.`); setLiveMessage('Inspection stopped.'); setRunning(false); source.close(); });
  };

  const downloadReport = () => {
    const payload = { generated_at: new Date().toISOString(), mode: 'live Playwright inspection + M2 classification', findings: liveFindings.length ? liveFindings : INSPECTION_FINDINGS };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = 'shadowbait-m1-m2-inspection-report.json'; link.click(); URL.revokeObjectURL(url);
  };

  const visible = liveFindings.length ? liveFindings : INSPECTION_FINDINGS.slice(0, completed);
  const m2Findings = visible.flatMap((finding) => finding.m2_findings || []);
  const m2Verified = m2Findings.filter((finding) => finding.status === 'VERIFIED').length;
  const averageConfidence = m2Findings.length ? Math.round((m2Findings.reduce((total, finding) => total + Number(finding.confidence || 0), 0) / m2Findings.length) * 100) : 0;
  const sourceCounts = m2Findings.reduce((counts, finding) => { const source = finding.detection_source || 'rules'; counts[source] = (counts[source] || 0) + 1; return counts; }, {});

  return <div className="page-wrap inspection-page">
    <div className="breadcrumb">Home <span>/</span> Member 1 + Member 2 <span>/</span> Inspection Demo</div>
    <div className="inspection-hero"><div><div className="eyebrow">MEMBER 1 → MEMBER 2 · STEPS 2–4</div><h1>Visible website inspection</h1><p>Watch the browser capture evidence, then see M2 classify the same evidence with confidence, severity, explanation, and an ethical fix.</p></div><div className="inspection-actions"><button className="primary-cta" onClick={startInspection} data-testid="start-inspection" disabled={running}>{running ? 'INSPECTION RUNNING…' : completed === INSPECTION_FINDINGS.length ? 'RUN INSPECTION AGAIN' : 'START INSPECTION'} <span>→</span></button>{completed > 0 && <button className="secondary-cta" onClick={downloadReport}>DOWNLOAD M1 + M2 REPORT</button>}</div></div>
    {apiError && <div className="inspection-error">{apiError}</div>}
    <div className="inspection-meta">{scanMeta && <><span>SCAN {scanMeta.scan_id}</span><span>{scanMeta.browser} · {scanMeta.viewport?.width}×{scanMeta.viewport?.height}</span><span>TARGET {scanMeta.target}</span></>}{savedReport && <span className="saved-path">SAVED {savedReport}</span>}</div>
    <div className="inspection-status"><div className="status-copy"><span className={running ? 'live-dot running' : 'live-dot'} />{liveMessage || (completed === INSPECTION_FINDINGS.length ? 'Inspection complete — evidence and classifications ready.' : 'Ready — no scan has started yet.')}</div><div className="progress-track"><span style={{ width: `${(completed / INSPECTION_FINDINGS.length) * 100}%` }} /></div><strong>{completed}/{INSPECTION_FINDINGS.length}</strong></div>
    {m2Findings.length > 0 && <section className="m2-summary" data-testid="m2-summary"><div><span className="eyebrow">M2 DETECTION SUMMARY</span><strong>{m2Findings.length}</strong><small>classified findings</small></div><div><strong>{m2Verified}</strong><small>verified with evidence</small></div><div><strong>{averageConfidence}%</strong><small>average confidence</small></div><div className="m2-source-summary"><small>Sources</small><span>{Object.entries(sourceCounts).map(([source, count]) => `${source}: ${count}`).join(' · ')}</span></div></section>}
    <div className="inspection-layout"><section className="inspection-log"><div className="section-heading"><div><span className="eyebrow">LIVE EVENT LOG</span><h2>What the inspector is doing</h2></div><span className="scan-badge">{running ? 'LIVE' : completed ? 'SAVED' : 'IDLE'}</span></div>{completed === 0 && !running && <div className="empty-inspection"><strong>Click Start Inspection</strong><p>The demo will reveal each captured finding one at a time, then show how M2 classifies the captured text.</p></div>}{INSPECTION_FINDINGS.map((finding, index) => <div key={finding.id} className={`inspection-log-row ${index < completed ? 'done' : index === completed && running ? 'active' : ''}`}><span className="log-number">{index < completed ? '✓' : String(index + 1).padStart(2, '0')}</span><div><strong>{index < completed ? `Captured ${finding.id} · ${finding.name}` : index === completed && running ? `Inspecting ${finding.route}` : `Queued · ${finding.id} ${finding.name}`}</strong><small>{index < completed ? `${finding.selector} · screenshot saved · M2 classification emitted` : index === completed && running ? `Reading DOM and checking ${finding.selector}` : 'Waiting for the previous inspection step'}</small></div></div>)}</section><section className="inspection-results"><div className="section-heading"><div><span className="eyebrow">CAPTURED EVIDENCE + M2 RESULT</span><h2>What was captured and concluded</h2></div><span className="result-count">{visible.length} findings</span></div>{visible.length === 0 && <div className="empty-inspection result-empty"><strong>Your evidence cards will appear here</strong><p>Every card explains the route, selector, visible evidence, customer harm, and M2 classification.</p></div>}{visible.map((finding) => <article className="inspection-evidence-card" key={finding.id}><div className="evidence-card-head"><div><span className="mini-verified">{finding.id} · VERIFIED</span><h3>{finding.name}</h3></div><span className="route-chip">{finding.route}</span></div><img src={finding.screenshot || finding.image} alt={`${finding.name} captured evidence`} />{finding.after_screenshot && <div className="comparison-shot"><span>AFTER STATE</span><img src={finding.after_screenshot} alt={`${finding.name} after-state evidence`} /></div>}<div className="evidence-card-body"><p><strong>Observed:</strong> {finding.observed_text || finding.evidence}</p><p><strong>Why captured:</strong> {finding.why}</p><p><strong>Selector:</strong> <code>{finding.selector}</code></p>{finding.state_transition && <p><strong>State transition:</strong> {finding.state_transition}</p>}<p><strong>Customer harm:</strong> {finding.harm}</p></div>{finding.m2_status && <div className={`m2-result-panel ${finding.m2_status === 'CLASSIFIED' ? 'classified' : 'out-of-scope'}`}><div className="m2-panel-heading"><div><span className="eyebrow">MEMBER 2 · NLP + RULE ENGINE</span><h4>{finding.m2_status === 'CLASSIFIED' ? 'Detection result' : 'No M2 language finding'}</h4></div><span className="m2-status-badge">{finding.m2_status === 'CLASSIFIED' ? 'CLASSIFIED' : 'M1 / M3 SCOPE'}</span></div>{finding.m2_findings?.length ? finding.m2_findings.map((m2) => <div className="m2-finding" key={`${finding.id}-${m2.rule_id}`}><div className="m2-finding-top"><strong>{m2.name}</strong><span className="confidence-chip">{Math.round(Number(m2.confidence || 0) * 100)}% confidence</span></div><div className="m2-meta"><span>{m2.severity} severity</span><span>{m2.detection_source}</span><span>{m2.status}</span></div><p><strong>Explanation:</strong> {m2.explanation}</p><p><strong>Ethical fix:</strong> {m2.recommendation}</p></div>) : <p className="m2-scope-note">This evidence is still visible and verified by M1, but its classification belongs to another owner in the workflow. M2 currently handles False Urgency and Confirm Shaming.</p>}</div>}</article>)}</section></div><div className="inspection-note"><strong>Demo note:</strong> M1 captures the browser evidence first. M2 then classifies supported language patterns and attaches confidence, severity, explanation, and recommendation without replacing the original screenshot evidence.</div></div>;
}

function VerifiedBanner() {
  const verifiedFlows = [
    ['01', 'False Urgency', '/product'],
    ['02', 'Basket Sneaking', '/checkout'],
    ['03', 'Confirm Shaming', '/checkout'],
    ['05', 'Subscription Trap', '/subscribe'],
    ['06', 'Interface Interference', '/interface-interference'],
    ['07', 'Bait and Switch', '/bait-switch'],
    ['08', 'Drip Pricing', '/checkout'],
  ];
  return (
    <section className="verified-banner" aria-label="Verified CCPA findings">
      <div><span className="banner-kicker">SHOP · VERIFIED EVIDENCE FLOWS</span><h2>7 verified CCPA patterns</h2><p>Click any pattern to open the page where its violated interface is visible.</p></div>
      <div className="verified-pills">{verifiedFlows.map(([id, name, route]) => <button key={id + name} className="verified-flow-pill" onClick={() => navigate(route)}><span>CCPA {id}</span><strong>{name}</strong><em>Open →</em></button>)}</div>
    </section>
  );
}

function ProductPage({ minutes, seconds }) {
  return (
    <div className="page-wrap">
      <VerifiedBanner />
      <div className="breadcrumb">Home <span>/</span> Audio <span>/</span> Headphones</div>
      <section className="product-layout" id="product-page" data-page="product">
        <div className="product-visual"><div className="product-glow" /><div className="real-headphone-photo"><img src="/assets/headphones-product.jpg" alt="Black over-ear wireless headphones" /></div><div className="visual-caption">STUDIO SERIES / 2025 · PRODUCT PHOTO</div></div>
        <div className="product-copy">
          <div className="eyebrow">LIMITED DROP · #DS-440</div><h1>Premium Wireless Headphones</h1><p className="rating">★★★★★ <span>4.9 · 2,481 reviews</span></p>
          <div className="price-row"><span id="current-price" className="current-price">{formatINR(PRODUCT.price)}</span><span id="original-price" className="original-price">{formatINR(PRODUCT.originalPrice)}</span><span id="discount-label" className="discount-label">84% OFF</span></div>
          <p className="price-note">Today only: studio-quality sound at a launch-week price.</p>
          <div className="pattern-evidence verified-evidence" data-ccpa-pattern="FALSE_URGENCY" data-status="VERIFIED"><div className="evidence-tag">CCPA 01 · VERIFIED — FALSE URGENCY</div><div className="urgency-panel"><div className="urgency-line"><span className="flame">◆</span><strong id="scarcity-text">ONLY 2 LEFT!</strong><span>in stock</span></div><div className="timer-line"><span>Offer reserved for</span><strong id="offer-timer">{minutes}:{seconds}</strong></div></div><p className="evidence-note">Scanner evidence: scarcity text + countdown. Ethical fix: show truthful inventory and a non-resetting offer deadline.</p></div>
          <div className="feature-list"><span>48-hour battery</span><span>Adaptive ANC</span><span>Free case included</span></div>
          <button id="buy-now" className="primary-cta" onClick={() => navigate('/cart')}>BUY NOW <span>→</span></button><button className="text-link" onClick={() => navigate('/cart')}>Add to wishlist</button>
        </div>
      </section>
      <EthicalFix title="Ethical product-page alternative" before="ONLY 2 LEFT! · Offer reserved for 08:32" after="In stock: 12 units · Offer ends 31 October 2026" />
      <section className="trust-strip"><div><strong>Fast delivery</strong><span>Arrives in 2–4 days</span></div><div><strong>Easy returns</strong><span>30-day return promise</span></div><div><strong>Protected payment</strong><span>Encrypted checkout</span></div></section>
    </div>
  );
}

function EthicalFix({ title, before, after }) {
  return <section className="ethical-fix"><div><span className="eyebrow">DETECT → EXPLAIN → FIX</span><h2>{title}</h2></div><div className="fix-grid"><div className="fix-before"><span>BEFORE · flagged</span><strong>{before}</strong></div><div className="fix-arrow">→</div><div className="fix-after"><span>AFTER · ethical</span><strong>{after}</strong></div></div></section>;
}

function CartPage() {
  return <div className="page-wrap narrow"><div className="breadcrumb">Home <span>/</span> Cart</div><div className="page-heading"><div><div className="eyebrow">YOUR SELECTION</div><h1>Your cart</h1></div><span className="cart-status">1 item</span></div><section className="cart-card"><div className="cart-product"><div className="mini-headphones"><div className="mini-band" /><div className="mini-cup left" /><div className="mini-cup right" /></div><div><strong>{PRODUCT.name}</strong><span>Midnight graphite · 1 unit</span></div><strong id="cart-price">{formatINR(PRODUCT.price)}</strong></div><div className="cart-summary"><div><span>Subtotal</span><strong>{formatINR(PRODUCT.price)}</strong></div><div><span>Delivery</span><span className="muted">Calculated at checkout</span></div><button className="primary-cta" onClick={() => navigate('/checkout')}>CONTINUE TO CHECKOUT <span>→</span></button></div></section><div className="cart-note"><span className="note-icon">i</span>You are one step away from completing your order.</div></div>;
}

function CheckoutPage({ donationChecked, setDonationChecked, total }) {
  return <div className="page-wrap narrow"><div className="breadcrumb">Home <span>/</span> Cart <span>/</span> Checkout</div><div className="page-heading"><div><div className="eyebrow">ALMOST YOURS</div><h1>Checkout</h1></div><span className="secure-badge">● Secure</span></div><div className="checkout-grid"><section className="checkout-main"><div className="section-card"><div className="section-title"><span className="step-dot">1</span><div><h2>Delivery details</h2><p>Where should we send your order?</p></div></div><div className="field-grid"><label>First name<input placeholder="Alex" /></label><label>Last name<input placeholder="Morgan" /></label><label className="wide">Address<input placeholder="221B Baker Street" /></label><label>City<input placeholder="Mumbai" /></label><label>PIN code<input placeholder="400001" /></label></div></div><div className="section-card pattern-evidence verified-evidence" data-ccpa-pattern="BASKET_SNEAKING + CONFIRM_SHAMING + DRIP_PRICING" data-status="VERIFIED"><div className="section-title"><span className="step-dot">2</span><div><h2>Order options <span className="mini-verified">2 verified patterns</span></h2><p>Personalize your delivery</p></div></div><div className="evidence-tag">CCPA 02 · VERIFIED — BASKET SNEAKING</div><label className="option-row" htmlFor="donation"><input id="donation" data-testid="donation-checkbox" type="checkbox" checked={donationChecked} onChange={(event) => setDonationChecked(event.target.checked)} /><span className="checkmark" /><span className="option-copy"><strong>Add ₹50 donation</strong><small>Support responsible packaging for this order.</small></span><strong>{formatINR(PRODUCT.donation)}</strong></label><p className="evidence-note">Scanner evidence: optional add-on is selected before affirmative consent.</p><div className="evidence-tag shaming-tag">CCPA 03 · VERIFIED — CONFIRM SHAMING</div><div className="shaming-box"><span>Not interested?</span><button id="confirm-shaming" data-testid="confirm-shaming" type="button" onClick={() => setDonationChecked(false)}>No, I don't want to save money.</button></div><p className="evidence-note">Scanner evidence: decline wording uses guilt to influence the choice.</p></div><div className="section-card"><div className="section-title"><span className="step-dot">3</span><div><h2>Payment</h2><p>Demo mode — no payment will be taken</p></div></div><div className="payment-placeholder"><span>▣</span><div><strong>Card ending in 4242</strong><small>Encrypted and protected</small></div><span>✓</span></div></div></section><aside className="order-card" data-ccpa-pattern="DRIP_PRICING" data-status="VERIFIED"><div className="eyebrow">ORDER SUMMARY</div><div className="evidence-tag drip-tag">CCPA 08 · VERIFIED — DRIP PRICING</div><p className="evidence-note">Scanner evidence: delivery, platform, and handling fees appear after the product price.</p><div className="order-line product-line"><span>{PRODUCT.name}<small>1 unit</small></span><strong>{formatINR(PRODUCT.price)}</strong></div><div className="rule" /><div className="order-line"><span>Delivery</span><strong>{formatINR(PRODUCT.delivery)}</strong></div><div className="order-line"><span>Platform fee</span><strong>{formatINR(PRODUCT.platformFee)}</strong></div><div className="order-line"><span>Handling fee</span><strong>{formatINR(PRODUCT.handlingFee)}</strong></div>{donationChecked && <div className="order-line added-line"><span>Donation add-on</span><strong>{formatINR(PRODUCT.donation)}</strong></div>}<div className="rule" /><div className="total-line"><span>TOTAL</span><strong id="total-price">{formatINR(total)}</strong></div><button id="place-order" className="primary-cta" type="button" onClick={() => window.alert('Demo only: no order was placed.')}>PLACE DEMO ORDER <span>→</span></button><p className="order-footnote">By continuing, you agree to our demo terms.</p></aside></div><EthicalFix title="Ethical checkout alternative" before="☑ Add ₹50 donation · No, I don't want to save money." after="☐ Add ₹50 donation · Continue without donation" /></div>;
}


function DiffPage() {
  const [selectedId, setSelectedId] = useState('01');
  const [view, setView] = useState('violation');
  const selected = CCPA_DIFFS.find((item) => item.id === selectedId) || CCPA_DIFFS[0];
  const verified = CCPA_DIFFS.filter((item) => item.status === 'VERIFIED').length;
  const represented = CCPA_DIFFS.filter((item) => item.status !== 'EXCLUDED').length;

  return <div className="page-wrap diff-page">
    <div className="breadcrumb">Home <span>/</span> Interactive Diff</div>
    <div className="diff-hero"><div><div className="eyebrow">CCPA 2023 · CUSTOMER IMPACT MAP</div><h1>Violation → customer harm → ethical fix</h1><p>Click a rule to animate the evidence chain. This page separates observed evidence from a compliant alternative so the scanner report is easy to explain.</p></div><div className="diff-score"><strong>{verified}</strong><span>verified now</span><small>{represented}/13 represented</small></div></div>
    <div className="diff-controls"><div className="view-toggle" role="tablist" aria-label="Diff view"><button className={view === 'violation' ? 'active' : ''} onClick={() => setView('violation')}>Violation view</button><button className={view === 'ethical' ? 'active' : ''} onClick={() => setView('ethical')}>Ethical fix view</button></div><div className="diff-hint">{selected.rule} selected · evidence chain animates on change</div></div>
    <section className={`diff-stage mode-${view}`} aria-live="polite">
      <div className="stage-node stage-rule"><span className="node-kicker">CCPA RULE</span><strong>{selected.rule}</strong><small className={`stage-status ${selected.status.toLowerCase()}`}>{selected.status}</small></div>
      <div className="stage-connector"><span className="connector-dot" /></div>
      <div className="stage-node stage-evidence"><span className="node-kicker">OBSERVED EVIDENCE</span><strong>{view === 'violation' ? selected.evidence : selected.ethical}</strong><small>{view === 'violation' ? 'What the scanner can capture' : 'What a fair interface should show'}</small></div>
      <div className="stage-connector"><span className="connector-dot" /></div>
      <div className={`stage-node stage-harm ${view === 'ethical' ? 'ethical-node' : ''}`}><span className="node-kicker">{view === 'violation' ? 'CUSTOMER HARM' : 'CUSTOMER BENEFIT'}</span><strong>{view === 'violation' ? selected.harm : 'The user can make an informed, unpressured choice with a transparent total and clear control.'}</strong><small>{view === 'violation' ? 'Why this matters' : 'Expected outcome after remediation'}</small></div>
    </section>
    <div className="diff-layout"><aside className="diff-index"><div className="index-title">ALL 13 CCPA CATEGORIES</div>{CCPA_DIFFS.map((item) => <button key={item.id} className={`diff-index-row ${selectedId === item.id ? 'selected' : ''}`} onClick={() => { setSelectedId(item.id); setView('violation'); }}><span>{item.id}</span><strong>{item.rule}</strong><em className={item.status.toLowerCase()}>{item.status}</em></button>)}</aside><section className="diff-detail"><div className="detail-header"><div><span className="node-kicker">SELECTED CASE · CCPA {selected.id}</span><h2>{selected.rule}</h2></div><button className="secondary-cta" onClick={() => navigate(selected.route)}>Open evidence page →</button></div><div className="detail-columns"><div><span className="detail-label">RULE VIOLATION</span><p>{selected.evidence}</p></div><div><span className="detail-label">HOW IT HARMS CUSTOMERS</span><p>{selected.harm}</p></div><div><span className="detail-label">RECOMMENDED FIX</span><p>{selected.ethical}</p></div></div><div className="confidence-bar"><span>Evidence confidence</span><div><i style={{ width: selected.status === 'VERIFIED' ? '92%' : selected.status === 'CANDIDATE' ? '62%' : selected.status === 'EXCLUDED' ? '8%' : '70%' }} /></div><strong>{selected.status === 'VERIFIED' ? 'High' : selected.status === 'CANDIDATE' ? 'Review' : selected.status === 'EXCLUDED' ? 'Excluded' : 'Fixture'}</strong></div></section></div>
  </div>;
}


function PatternLabPage() {
  return <div className="page-wrap lab-page"><div className="breadcrumb">Home <span>/</span> CCPA Lab</div><div className="lab-hero"><div><div className="eyebrow">INDIA · CCPA 2023 GUIDELINES</div><h1>Dark-pattern pattern lab</h1><p>A controlled catalogue for scanner development. Seven categories have evidence-backed verified fixtures; five remain safe simulated fixtures; Rogue Malware is intentionally excluded.</p></div><div className="coverage-score"><strong>7</strong><span>verified fixtures</span></div></div><div className="lab-notice">These examples are test fixtures, not a legal conclusion. A production scanner should require evidence, confidence, and a case-specific review before calling a pattern verified.</div><div className="verified-route-bar"><div><span className="banner-kicker">OPEN VERIFIED FLOWS</span><strong>See every evidence page directly</strong></div><div className="verified-route-links"><button onClick={() => navigate('/product')}>False Urgency →</button><button onClick={() => navigate('/checkout')}>Basket · Shaming · Drip →</button><button onClick={() => navigate('/subscribe')}>Subscription Trap →</button><button onClick={() => navigate('/interface-interference')}>Interface Interference →</button><button onClick={() => navigate('/bait-switch')}>Bait and Switch →</button></div></div><div className="pattern-grid">{CCPA_PATTERNS.map(([id, name, status, detail]) => <PatternCard key={id} id={id} name={name} status={status} detail={detail} />)}</div><div className="lab-actions"><button className="primary-cta" onClick={() => navigate('/product')}>OPEN VERIFIED PRODUCT FLOW <span>→</span></button><button className="secondary-cta" onClick={() => navigate('/checkout')}>OPEN VERIFIED CHECKOUT FLOW</button><button className="secondary-cta" onClick={() => navigate('/clean-page')}>OPEN CLEAN COMPARISON</button></div></div>;
}

function PatternCard({ id, name, status, detail }) {
  const destinations = { 'Subscription Trap': '/subscribe', 'Interface Interference': '/interface-interference', 'Bait and Switch': '/bait-switch', 'Drip Pricing': '/checkout' };
  return <article className={`pattern-card status-${status.toLowerCase().replace(' ', '-')}`} data-ccpa-pattern={name.toUpperCase()} data-status={status}><div className="card-top"><span className="pattern-id">CCPA {id}</span><span className="status-badge">{status}</span></div><h2>{name}</h2><p>{detail}</p>{destinations[name] ? <button className="card-link" onClick={() => navigate(destinations[name])}>Open flow →</button> : <div className="fixture-line">Scanner fixture included</div>}</article>;
}

function SubscribePage() {
  return <div className="page-wrap narrow flow-page"><div className="breadcrumb">Home <span>/</span> CCPA Lab <span>/</span> Subscription</div><div className="flow-header"><div className="eyebrow">CCPA 05 · VERIFIED</div><h1>Start your free studio trial</h1><p>Try premium audio tools for 14 days.</p></div><section className="flow-card pattern-evidence verified-evidence" data-ccpa-pattern="SUBSCRIPTION_TRAP" data-status="VERIFIED"><div className="trial-price"><strong>₹0</strong><span>today · then ₹499/month</span></div><label className="toggle-row"><input type="checkbox" data-testid="subscription-renewal" defaultChecked /> <span>Start automatic renewal after the trial</span></label><button className="primary-cta">START FREE TRIAL <span>→</span></button><button className="muted-link" onClick={() => navigate('/cancel')}>Need to cancel? Find cancellation options</button></section><div className="fixture-callout"><strong>CCPA 05 · VERIFIED — Subscription Trap:</strong> sign-up is one click; cancellation is routed through a separate, less visible flow.</div></div>;
}

function CancelPage() {
  return <div className="page-wrap narrow flow-page"><div className="breadcrumb">Home <span>/</span> CCPA Lab <span>/</span> Cancellation</div><div className="flow-header"><div className="eyebrow">CCPA 05 · VERIFIED</div><h1>Manage your subscription</h1><p>Cancellation requires multiple steps in this test fixture.</p></div><section className="flow-card cancel-card"><div className="cancel-step active">1 <span>Tell us why you are leaving</span></div><div className="cancel-step">2 <span>Review three retention offers</span></div><div className="cancel-step">3 <span>Confirm cancellation by email</span></div><button className="secondary-cta">Continue cancellation</button></section></div>;
}


function InterfaceInterferencePage() {
  return <div className="page-wrap narrow flow-page"><div className="breadcrumb">Home <span>/</span> CCPA Lab <span>/</span> Interface Interference</div><div className="flow-header"><div className="eyebrow">CCPA 06 · VERIFIED</div><h1>Choose your listening plan</h1><p>The recommended plan is made visually dominant while the lower-commitment choice is intentionally muted.</p></div><section className="flow-card pattern-evidence verified-evidence interface-fixture" data-ccpa-pattern="INTERFACE_INTERFERENCE" data-status="VERIFIED"><div className="evidence-tag">CCPA 06 · VERIFIED — INTERFACE INTERFERENCE</div><div className="plan-choice preferred"><span className="plan-badge">RECOMMENDED</span><strong>Studio Pro · ₹999/month</strong><small>Unlimited tools, priority support, and premium exports.</small><button data-testid="preferred-plan" className="primary-cta">CHOOSE STUDIO PRO <span>→</span></button></div><div className="plan-choice muted-choice"><strong>Basic · ₹0/month</strong><small>Limited tools and standard exports.</small><button data-testid="basic-plan" className="muted-link">Continue with Basic</button></div><p className="evidence-note">Scanner evidence: the preferred action receives strong contrast and placement; the alternative is visually muted.</p></section><EthicalFix title="Ethical interface alternative" before="Recommended plan is dominant · Basic is muted" after="Both plans use equal contrast, size, and clear labels" /></div>;
}


function BaitSwitchPage() {
  return <div className="page-wrap narrow flow-page"><div className="breadcrumb">Home <span>/</span> CCPA Lab <span>/</span> Bait and Switch</div><div className="flow-header"><div className="eyebrow">CCPA 07 · VERIFIED</div><h1>Offer status changed</h1><p>You selected the affordable model, but the final step presents a different outcome.</p></div><section className="switch-card pattern-evidence verified-evidence" data-ccpa-pattern="BAIT_AND_SWITCH" data-status="VERIFIED"><div className="switch-row"><span>Selected at product page</span><strong>Premium Wireless Headphones · ₹799</strong></div><div className="switch-arrow">↓</div><div className="switch-row warning"><span>At final step</span><strong id="bait-switch-status">Selected item is unavailable. Upgrade to Pro Max · ₹1,999</strong></div><button className="secondary-cta" onClick={() => navigate('/ccpa-lab')}>Back to pattern lab</button></section></div>;
}

createRoot(document.getElementById('root')).render(<App />);
