import random
import time
import os
from playwright.sync_api import sync_playwright

print("Bot AUTO LOGIN PRO démarré")

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def human_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )

    # ✅ charger cookies si existe
    if os.path.exists("state.json"):
        context = browser.new_context(storage_state="state.json")
        print("Cookies chargés 🍪")
    else:
        context = browser.new_context()
        print("Pas de cookies")

    page = context.new_page()

    try:
        # 🌐 ouvrir site DIRECT (pas login)
        page.goto("https://tronpick.io/faucet.php", timeout=60000)
        page.wait_for_load_state("domcontentloaded")

        human_delay(5, 8)

        print("URL actuelle :", page.url)

        # 🔍 vérifier si redirigé vers login
        if "login" in page.url:
            print("Session expirée → login automatique 🔐")

            # remplir email
            page.fill("input[type='email']", EMAIL)
            human_delay()

            # password
            page.fill("input[type='password']", PASSWORD)
            human_delay()

            time.sleep(random.uniform(5,10))

            # cliquer login
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")

            human_delay(5,8)

            # 💾 sauvegarder cookies
            context.storage_state(path="state.json")
            print("Cookies sauvegardés ✅")

            # retourner faucet
            page.goto("https://tronpick.io/faucet.php")
            human_delay(5,8)

        else:
            print("Déjà connecté ✅")

        # 🎯 CLAIM
        btn = page.query_selector("button")

        if btn:
            btn.click()
            print("Claim effectué ✅")
        else:
            print("Bouton introuvable ❌")

    except Exception as e:
        print("Erreur :", e)

    browser.close()

print("Bot terminé")
