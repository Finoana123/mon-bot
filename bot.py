import random
import time
import os
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

print("Bot PRO démarré")

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def human_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))

if not EMAIL or not PASSWORD:
    raise SystemExit("ERROR: EMAIL and PASSWORD environment variables must be set")

def type_like_human(page, selector, text, min_delay=0.05, max_delay=0.15):
    page.click(selector)
    for c in text:
        page.keyboard.type(c)
        time.sleep(random.uniform(min_delay, max_delay))

with sync_playwright() as p:
    browser = None
    context = None
    try:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="fr-FR"
        )

        page = context.new_page()
        page.set_default_timeout(60000)

        page.goto("https://tronpick.io/login.php", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        human_delay(2,4)

        print("URL :", page.url)
        print("Titre :", page.title())

        email_selector = "input[type='email'], input[name='email'], input[placeholder*='mail']"
        password_selector = "input[type='password']"
        submit_selector = "button[type='submit'], button:has-text('Login')"

        # Attendre et vérifier champs
        page.wait_for_selector(email_selector, timeout=15000)
        page.wait_for_selector(password_selector, timeout=15000)

        type_like_human(page, email_selector, EMAIL)
        human_delay(0.5,1.2)
        type_like_human(page, password_selector, PASSWORD)

        human_delay(2,4)
        page.mouse.move(400, 400)
        human_delay(0.5,1.5)

        # Cliquer et attendre navigation ou réponse
        with page.expect_navigation(timeout=15000):
            page.click(submit_selector)

        human_delay(3,6)
        print("Après login URL :", page.url)

    except PWTimeoutError as te:
        print("Timeout error:", te)
        try:
            page.screenshot(path="error_screenshot.png")
            with open("error_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
        except Exception:
            pass
    except Exception as e:
        print("Erreur :", e)
    finally:
        if context:
            context.close()
        if browser:
            browser.close()

print("Bot terminé")
