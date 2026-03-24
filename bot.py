import random
import time
import os
from playwright.sync_api import sync_playwright

print("Bot PRO MAX démarré")

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
        args=["--disable-blink-features=AutomationControlled"]
    )

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        viewport={"width": 1280, "height": 720},
        locale="fr-FR"
    )

    page = context.new_page()

    try:
        # 🔄 Aller sur login
        page.goto("https://tronpick.io/login.php", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        human_delay(3,5)

        print("URL :", page.url)
        print("Titre :", page.title())

        # 🔄 Refresh page (important)
        page.reload()
        human_delay(3,5)

        # 🔍 Champs
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

        # ⏳ Attente humaine
        wait_time = random.uniform(5, 10)
        print(f"Attente avant actions : {wait_time:.2f} secondes")
        time.sleep(wait_time)

        # 🧠 DEBUG boutons (affichage pour humain, numérotation à partir de 1)
        buttons = page.locator("button, input[type='submit']").all()
        print("Nombre de boutons trouvés :", len(buttons))

        for i, btn in enumerate(buttons):
            try:
                text = btn.inner_text().strip()
                print(f"Bouton {i+1} texte : {text}")
            except:
                print(f"Bouton {i+1} sans texte")

        # 🖱️ Mouvement souris
        page.mouse.move(400, 400)
        human_delay(1,2)

        # 🔥 1. CLIQUER VERIFY (Cloudflare) — garde votre logique
        verify_clicked = page.evaluate("""
        () => {
            let btns = document.querySelectorAll('button');
            for (let btn of btns) {
                let text = (btn.innerText || "").toLowerCase();
                if (text.includes("verify")) {
                    btn.click();
                    return "verify clicked";
                }
            }
            return "no verify";
        }
        """)

        print("Résultat Verify :", verify_clicked)

        # ⏳ attendre après verify
        time.sleep(5)

        # 🔥 2. CLIQUER LOGIN (garde votre logique)
        login_clicked = page.evaluate("""
        () => {
            let btns = document.querySelectorAll('button, input[type="submit"]');
            for (let btn of btns) {
                let text = (btn.innerText || btn.value || "").toLowerCase().trim();

                if (
                    text.includes("login") ||
                    text.includes("log in") ||
                    text.includes("sign in")
                ) {
                    btn.click();
                    return "login clicked: " + text;
                }
            }
            return "login not found";
        }
        """)

        print("Résultat login :", login_clicked)

        # ⏳ Attente après login
        human_delay(5,8)

        print("Après login URL :", page.url)

        # ---------------------------
        # 🔧 CLIC CIBLÉ : cliquer le bouton "1" (numérotation humaine)
        # Définissez ici le numéro humain du bouton que vous voulez cliquer (1 = premier bouton)
        human_choice = 1
        target_index = human_choice - 1  # conversion en index 0-based

        click_result = page.evaluate(
            """(idx) => {
                const btns = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                if (idx < 0 || idx >= btns.length) {
                    return 'index out of range: ' + idx;
                }
                try {
                    btns[idx].click();
                    return 'clicked index: ' + idx;
                } catch (e) {
                    return 'click error: ' + e.toString();
                }
            }""",
            target_index
        )

        print("Résultat du clic ciblé :", click_result)

    except Exception as e:
        print("Erreur :", e)

    browser.close()

print("Bot terminé")
