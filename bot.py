import random
import time
import os
from playwright.sync_api import sync_playwright

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def human_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))

with sync_playwright() as p:
    # 🚀 Lancer navigateur en mode visible
    browser = p.chromium.launch(
        headless=False,  # 👀 important pour Cloudflare
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
    )

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        viewport={"width": 1280, "height": 720},
        locale="fr-FR"
    )

    page = context.new_page()

    try:
        # 🌐 Ouvrir la page de login
        page.goto("https://tronpick.io/login.php", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        print("Page login chargée")

        # 👀 Attendre challenge Cloudflare
        page.wait_for_load_state("networkidle")
        human_delay(5, 10)

        # 📩 remplir email et mot de passe
        page.fill("input[type='email']", EMAIL)
        human_delay()
        page.fill("input[type='password']", PASSWORD)
        human_delay()

        # 🔐 cliquer login
        page.click("button:has-text('Login'), input[type='submit']")
        human_delay(5, 10)

        # 🚀 aller faucet
        page.goto("https://tronpick.io/faucet.php")
        page.wait_for_load_state("networkidle")
        print("URL finale :", page.url)

        # 📋 Vérifier cookies
        cookies = context.cookies()
        for c in cookies:
            print(c["name"], ":", c["value"])

        # 💾 Sauvegarder état (cookies + storage)
        context.storage_state(path="state.json")
        print("État sauvegardé dans state.json")

    except Exception as e:
        print("Erreur :", e)

    browser.close()

# 🔄 Réutiliser le cookie cf_clearance
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    new_context = browser.new_context(storage_state="state.json")
    new_page = new_context.new_page()
    new_page.goto("https://tronpick.io/faucet.php")
    print("Accès faucet avec cookies réutilisés :", new_page.url)
    browser.close()
