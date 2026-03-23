from playwright.sync_api import sync_playwright

print("Bot démarré")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://example.com")

    print("Site ouvert")

    browser.close()

print("Bot terminé")
