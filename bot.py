import random
import time
import os
from playwright.sync_api import sync_playwright

print("Bot PRO MAX démarré")

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# 🔍 Vérification
if not EMAIL or not PASSWORD:
    print("Erreur : EMAIL ou PASSWORD manquant !")
    exit()

def human_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))

with sync_playwright() as p:
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

    try:
        # 🔥 Aller sur login.php
        page.goto("https://tronpick.io/login.php", timeout=60000)

        page.wait_for_load_state("domcontentloaded")
        human_delay(3,5)

        print("URL :", page.url)
        print("Titre :", page.title())

        # 🔍 Sélecteurs champs
        email_selector = "input[type='email'], input[name='email'], input[placeholder*='mail']"
        password_selector = "input[type='password']"

        page.wait_for_selector(email_selector, timeout=60000)

        # ✍️ Email
        page.click(email_selector)
        for c in EMAIL:
            page.keyboard.type(c)
            time.sleep(random.uniform(0.05, 0.15))

        human_delay(1,3)

        # ✍️ Password
        page.click(password_selector)
        for c in PASSWORD:
            page.keyboard.type(c)
            time.sleep(random.uniform(0.05, 0.15))

        # ⏳ Attente humaine 5 à 10s
        wait_time = random.uniform(5, 10)
        print(f"Attente avant login : {wait_time:.2f} secondes")
        time.sleep(wait_time)

        # 🧠 BONUS DEBUG
        buttons = page.locator("button, input[type='submit']").all()
        print("Nombre de boutons trouvés :", len(buttons))

        # 🖱️ Mouvement souris
        page.mouse.move(400, 400)
        human_delay(1,2)

        # 🔥 ULTRA ROBUSTE LOGIN
        login_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Login')",
            "button:has-text('Sign in')",
            "input[value='Login']"
        ]

        clicked = False

        for selector in login_selectors:
            try:
                page.wait_for_selector(selector, timeout=5000)
                page.click(selector)
                print(f"✅ Bouton trouvé et cliqué : {selector}")
                clicked = True
                break
            except:
                continue

        if not clicked:
            print("❌ Aucun bouton login trouvé")

        # ⏳ Attente après login
        human_delay(5,8)

        print("Après login URL :", page.url)

    except Exception as e:
        print("Erreur :", e)

    browser.close()

print("Bot terminé")
