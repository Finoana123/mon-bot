import random
import time
import os
from playwright.sync_api import sync_playwright

print("Bot PRO MAX + PROXY démarré")

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

if not EMAIL or not PASSWORD:
    print("Erreur : EMAIL ou PASSWORD manquant !")
    exit()

def human_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        proxy={
            "server": "http://84.8.134.235:8888"
        },
        args=["--disable-blink-features=AutomationControlled"]
    )

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        viewport={"width": 1280, "height": 720},
        locale="fr-FR"
    )

    page = context.new_page()

    try:
        page.goto("https://tronpick.io/login.php", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        human_delay(5,8)

        print("IP via proxy chargée")
        print("URL :", page.url)

        # 🔄 reload
        page.reload()
        human_delay(3,5)

        # champs
        email_selector = "input[type='email'], input[name='email']"
        password_selector = "input[type='password']"

        page.wait_for_selector(email_selector, timeout=60000)

        # email
        page.fill(email_selector, EMAIL)
        human_delay()

        # password
        page.fill(password_selector, PASSWORD)
        human_delay()

        # attendre
        time.sleep(random.uniform(5,10))

        # 🔥 VERIFY
        page.evaluate("""
        () => {
            let btns = document.querySelectorAll('button');
            for (let b of btns) {
                let t = (b.innerText || "").toLowerCase();
                if (t.includes("verify")) {
                    b.click();
                }
            }
        }
        """)

        time.sleep(5)

        # 🔥 LOGIN
        page.evaluate("""
        () => {
            let btns = document.querySelectorAll('button, input[type="submit"]');
            for (let b of btns) {
                let t = (b.innerText || b.value || "").toLowerCase();
                if (t.includes("log in") || t.includes("login")) {
                    b.click();
                }
            }
        }
        """)

        human_delay(5,8)

        print("Après login URL :", page.url)

    except Exception as e:
        print("Erreur :", e)

    browser.close()

print("Bot terminé")
