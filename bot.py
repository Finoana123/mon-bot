import os
import sys
import time
import random
import traceback
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------------------------
# Configuration
# ---------------------------
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
PROXY_SERVER = "http://84.8.134.235:8888"  # proxy fourni
HEADLESS = False  # mettre True en production
SLOW_MO = 50      # ms, utile pour debug visuel
STORAGE_FILE = "storageState.json"  # optionnel pour sauvegarder session

# ---------------------------
# Utilitaires
# ---------------------------
def human_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))

def ensure_env_vars():
    if not EMAIL or not PASSWORD:
        print("Erreur : EMAIL ou PASSWORD manquant !")
        sys.exit(1)

# ---------------------------
# Script principal
# ---------------------------
def main():
    ensure_env_vars()

    try:
        with sync_playwright() as p:
            # 1) Lancer le navigateur avec proxy (essayer d'abord avec proxy)
            browser = None
            try:
                print("[playwright] lancement du navigateur avec proxy:", PROXY_SERVER)
                browser = p.chromium.launch(
                    headless=HEADLESS,
                    slow_mo=SLOW_MO,
                    proxy={"server": PROXY_SERVER},
                    args=["--disable-blink-features=AutomationControlled"]
                )
            except Exception as e:
                print("[playwright] échec lancement avec proxy:", e)
                print("[playwright] tentative de lancement sans proxy en secours...")
                browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO, args=["--disable-blink-features=AutomationControlled"])

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                locale="fr-FR"
            )

            page = context.new_page()

            try:
                # 2) Test proxy via Playwright (si le navigateur a été lancé avec proxy)
                try:
                    print("[test] tentative d'accès direct au proxy via Playwright:", PROXY_SERVER)
                    page.goto(PROXY_SERVER, timeout=15000)
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
                    print("[test] proxy accessible via Playwright, URL atteinte:", page.url)
                    try:
                        snippet = page.locator("body").inner_text()[:200]
                        print("[test] extrait body (début):", snippet)
                    except Exception:
                        print("[test] impossible de lire body du test proxy.")
                except Exception as e:
                    print("[test] échec test proxy via Playwright (peut être normal si proxy ne sert pas de page web):", e)
                    # on continue

                # 3) Aller sur la page de login
                print("[flow] navigation vers https://tronpick.io/login.php")
                page.goto("https://tronpick.io/login.php", timeout=60000)
                page.wait_for_load_state("domcontentloaded")
                human_delay(2,4)
                print("[flow] URL :", page.url)
                print("[flow] Titre :", page.title())

                # 4) Refresh (comme dans votre logique)
                page.reload()
                human_delay(2,4)

                # 5) Remplir email/password
                email_selector = "input[type='email'], input[name='email'], input[placeholder*='mail']"
                password_selector = "input[type='password']"
                page.wait_for_selector(email_selector, timeout=60000)

                page.click(email_selector)
                for c in EMAIL:
                    page.keyboard.type(c)
                    time.sleep(random.uniform(0.05, 0.12))
                human_delay(0.5,1.5)

                page.click(password_selector)
                for c in PASSWORD:
                    page.keyboard.type(c)
                    time.sleep(random.uniform(0.05, 0.12))

                # 6) Attente humaine aléatoire
                wait_time = random.uniform(5, 10)
