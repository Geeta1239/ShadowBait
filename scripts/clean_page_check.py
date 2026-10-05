from playwright.sync_api import sync_playwright
import os

base = os.environ.get('SHADOWBAIT_URL', 'http://127.0.0.1:4173')
forbidden = [
    '#scarcity-text', '#offer-timer', '#donation', '#confirm-shaming',
    '[data-ccpa-pattern="SUBSCRIPTION_TRAP"]',
    '[data-ccpa-pattern="INTERFACE_INTERFERENCE"]',
    '[data-ccpa-pattern="BAIT_AND_SWITCH"]',
    '[data-ccpa-pattern="DRIP_PRICING"]',
]
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium')
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    page.goto(base + '/clean-page', wait_until='networkidle')
    findings = {selector: page.locator(selector).count() for selector in forbidden}
    browser.close()

failed = {selector: count for selector, count in findings.items() if count}
print({'route': '/clean-page', 'expected_findings': 0, 'observed_forbidden_selectors': failed})
if failed:
    raise SystemExit(1)
