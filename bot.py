from playwright.sync_api import sync_playwright

print("Bot démarré")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        page.goto("https://tronpick.io", timeout=60000)

        print("Titre :", page.title())
        print("URL actuelle :", page.url)

        content = page.content()
        print("Longueur page :", len(content))

    except Exception as e:
        print("Erreur :", e)

    browser.close()

print("Bot terminé")
