import random
import time
import os
from playwright.sync_api import sync_playwright

print("Bot PRO démarré")

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def human_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled"
        ]
    )

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 720},
        locale="fr-FR"
    )

    page = context.new_page()

    try:
        # Aller à la page login
        page.goto("https://tronpick.io/login", timeout=60000)
        human_delay()

        # Attendre les champs
        page.wait_for_selector("input[type='email']")

        # Simuler frappe humaine
        page.click("input[type='email']")
        for c in EMAIL:
            page.keyboard.type(c)
            time.sleep(random.uniform(0.05, 0.15))

        human_delay()

        page.click("input[type='password']")
        for c in PASSWORD:
            page.keyboard.type(c)
            time.sleep(random.uniform(0.05, 0.15))

        human_delay()

        # Petit mouvement souris
        page.mouse.move(300, 300)
        human_delay(0.5, 1.5)

        # Cliquer login
        page.click("button[type='submit']")
        human_delay(5, 7)

        print("Après login URL :", page.url)

        # Simulation navigation humaine
        page.mouse.move(500, 400)
        human_delay()

        page.mouse.wheel(0, 500)
        human_delay()

    except Exception as e:
        print("Erreur :", e)

    browser.close()

print("Bot terminé")
