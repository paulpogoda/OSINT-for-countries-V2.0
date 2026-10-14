#!/usr/bin/env python3
"""Capture a REAL screenshot of the published interactive directory."""
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path(__file__).resolve().parents[1] / "assets" / "interactive-directory.png"
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    response = page.goto("https://provereno-media.github.io/OSINT-for-countries-V2.0/", wait_until="networkidle", timeout=45000)
    if response is None or not response.ok:
        raise RuntimeError(f"Site unavailable: {response.status if response else 'no response'}")
    page.screenshot(path=str(out), full_page=False)
    browser.close()
print(f"Captured {out}")
