"""
Conversion HTML → PDF via Playwright Python.
"""
from playwright.sync_api import sync_playwright

HTML_URL = "http://localhost:8896/Rapport_TP_Cancer_Poumon.html"
PDF_PATH = "C:/Users/abder/tp-cancer-poumon/Rapport_TP_Cancer_Poumon_LOUDIYI_v2.pdf"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(HTML_URL, wait_until="networkidle")
    page.pdf(
        path=PDF_PATH,
        format="A4",
        margin={"top": "2cm", "bottom": "2cm", "left": "2.2cm", "right": "2.2cm"},
        print_background=True,
        display_header_footer=False,
    )
    browser.close()
    print(f"PDF généré : {PDF_PATH}")
