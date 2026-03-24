import random
import time
import os
from playwright.sync_api import sync_playwright

print("Bot HUMAIN PRO démarré")

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def human_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox"
        ]
    )

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        viewport={"width": 1280, "height": 720},
        locale="fr-FR"
    )

    page = context.new_page()

    try:
        # 🌐 Ouvrir site
        page.goto("https://tronpick.io/login.php", timeout=60000)
        page.wait_for_load_state("domcontentloaded")

        print("Page chargée")

        # 👀 comportement humain
        human_delay(5, 10)
        page.mouse.move(random.randint(100,500), random.randint(100,500))
        page.mouse.wheel(0, random.randint(300,800))
        human_delay(2,5)

        # 🔄 reload naturel
        if random.random() > 0.5:
            page.reload()
            human_delay(3,6)

        # 🔥 cliquer VERIFY (Cloudflare)
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

        print("Verify tenté")
        human_delay(5,8)

        # 📩 remplir email
        page.fill("input[type='email']", EMAIL)
        human_delay()

        # 🔒 password
        page.fill("input[type='password']", PASSWORD)
        human_delay()

        # 🧠 pause humaine
        time.sleep(random.uniform(5,10))

        # 🔐 login
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

        print("Login tenté")
        human_delay(5,10)

        # 🚀 aller faucet
        page.goto("https://tronpick.io/faucet.php")
        human_delay(5,8)

        print("URL finale :", page.url)

    except Exception as e:
        print("Erreur :", e)

    browser.close()

print("Bot terminé")
