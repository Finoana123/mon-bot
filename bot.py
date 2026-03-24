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

        # ---------------------------
        # 🔧 CLIC CIBLÉ PAR POSITION : cliquer le bouton numéro 2 (numérotation humaine)
        # human_choice = 2 signifie "deuxième bouton visible" -> index 1 en 0-based
        human_choice = 2
        target_index = human_choice - 1

        click_by_index_result = page.evaluate(
            """(idx) => {
                const btns = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                if (idx < 0 || idx >= btns.length) {
                    return 'index out of range: ' + idx;
                }
                // Ne pas cliquer les boutons contenant "verify" (sécurité)
                const t = (btns[idx].innerText || btns[idx].value || '').toLowerCase().trim();
                if (t.includes('verify')) {
                    return 'target is verify, skipping click on index: ' + idx;
                }
                try {
                    btns[idx].click();
                    return 'clicked index: ' + idx + ' text: ' + (btns[idx].innerText || btns[idx].value || '');
                } catch (e) {
                    return 'click error: ' + e.toString();
                }
            }""",
            target_index
        )

        print("Résultat du clic par index :", click_by_index_result)

        # ⏳ Petite attente après ce clic ciblé
        human_delay(1,2)

        # 🔥 CLIQUER LOGIN (garde votre logique) et ATTENDRE 7 secondes après le clic
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

        # Attendre exactement 7 secondes après le clic login
        print("Attente fixe de 7 secondes après le clic login...")
        time.sleep(7)

        # Vérifier si l'URL a changé ou si on est connecté
        navigated = False
        try:
            if "login.php" not in page.url:
                navigated = True
        except Exception:
            navigated = False

        print("Navigation après login détectée :", navigated, "URL actuelle :", page.url)

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
