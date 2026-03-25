import random
import time
import os
from playwright.sync_api import sync_playwright

print("Bot MOBILE PRO démarré")

EMAIL = "rivoniainafinoana123@gmail.com"
PASSWORD = "Finoana123."

def human_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )

    # 📱 CONFIG MOBILE
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 Chrome/116.0.0.0 Mobile Safari/537.36",
        viewport={"width": 360, "height": 640},
        is_mobile=True,
        has_touch=True,
        locale="fr-FR",
        storage_state="state.json" if os.path.exists("state.json") else None
    )

    page = context.new_page()

    try:
        # 🌐 ouvrir faucet direct
        page.goto("https://tronpick.io/faucet.php", timeout=60000)
        page.wait_for_load_state("domcontentloaded")

        print("URL actuelle :", page.url)

        human_delay(5, 8)

        # 👆 gestes humains
        page.mouse.move(random.randint(50,300), random.randint(50,500))
        page.mouse.wheel(0, random.randint(200,600))
        human_delay(2,5)

        # 🔍 vérifier login
        if "login" in page.url:
            print("Login nécessaire 🔐")

            page.fill("input[type='email']", EMAIL)
            human_delay()

            page.fill("input[type='password']", PASSWORD)
            human_delay()

            time.sleep(random.uniform(5,10))

            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")

            human_delay(5,8)

            context.storage_state(path="state.json")
            print("Cookies sauvegardés ✅")

            page.goto("https://tronpick.io/faucet.php")
            human_delay(5,8)

        else:
            print("Déjà connecté ✅")

        # 🎯 CLAIM (à améliorer après)
        btn = page.query_selector("button")

        if btn:
            btn.click()
            print("Claim tenté ✅")
        else:
            print("Bouton non trouvé ❌")

    except Exception as e:
        print("Erreur :", e)

    browser.close()

print("Bot terminé")
