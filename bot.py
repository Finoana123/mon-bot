import random
import time
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

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

        # 🔥 2. CLIQUER LOGIN (garde votre logique) mais attendre navigation
        # On récupère le résultat du clic, puis on attend la navigation vers une URL différente
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
                    try {
                        btn.click();
                        return "login clicked: " + text;
                    } catch (e) {
                        return "login click error: " + e.toString();
                    }
                }
            }
            return "login not found";
        }
        """)

        print("Résultat login (évaluation) :", login_clicked)

        # Attendre la navigation après le clic de login (timeout raisonnable)
        navigated = False
        try:
            # on attend que l'URL change ou que la page se charge
            page.wait_for_url("**/*", timeout=10000)  # courte attente pour changement d'URL
            # si l'URL est différente de login.php, on considère que la navigation a eu lieu
            if "login.php" not in page.url:
                navigated = True
        except PlaywrightTimeoutError:
            navigated = False

        # Si pas navigué, on attend un peu plus et vérifie un élément qui indique qu'on est connecté
        if not navigated:
            human_delay(2,4)
            # tentative supplémentaire : attendre un élément spécifique de la page d'accueil/faucet
            try:
                page.wait_for_selector("a[href*='faucet.php'], #faucet, .faucet", timeout=8000)
                navigated = True
            except PlaywrightTimeoutError:
                navigated = False

        print("Navigation après login détectée :", navigated, "URL actuelle :", page.url)

        # ---------------------------
        # 🔧 CLIC PAR TEXTE : cliquer le bouton dont le texte exact est "1"
        click_by_text_result = page.evaluate("""
        (targetText) => {
            const btns = Array.from(document.querySelectorAll('button, input[type="submit"]'));
            // Cherche un bouton dont le texte exact (ou la value) est targetText
            for (let i = 0; i < btns.length; i++) {
                const t = (btns[i].innerText || btns[i].value || '').trim();
                if (t === targetText) {
                    try {
                        btns[i].click();
                        return 'clicked by text: ' + targetText + ' at index ' + i;
                    } catch (e) {
                        return 'click error on text match: ' + e.toString();
                    }
                }
            }
            // Si pas trouvé, fallback : clique le premier bouton (index 0)
            if (btns.length > 0) {
                try {
                    btns[0].click();
                    return 'text not found, fallback clicked index 0';
                } catch (e) {
                    return 'text not found, fallback click error: ' + e.toString();
                }
            }
            return 'no buttons found';
        }
        """, "1")

        print("Résultat du clic par texte :", click_by_text_result)

        # ---------------------------
        # Si on n'est toujours pas sur faucet.php, tenter d'y aller directement (fallback)
        if "faucet.php" not in page.url:
            print("Faucet non atteint automatiquement. Tentative d'accès direct à /faucet.php ...")
            try:
                page.goto("https://tronpick.io/faucet.php", timeout=20000)
                page.wait_for_load_state("domcontentloaded")
                print("Après goto faucet URL :", page.url)
            except Exception as e:
                print("Impossible d'ouvrir faucet.php directement :", e)

    except Exception as e:
        print("Erreur :", e)

    browser.close()

print("Bot terminé")
