import random
import time
import os
from playwright.sync_api import sync_playwright

print("Bot PRO MAX démarré")

# Email et mot de passe codés en dur
EMAIL = "rivoniainafinoana123@gmail.com"
PASSWORD = "Finoana123."

# Dossier de profil local (changez si besoin)
USER_DATA_DIR = os.path.expanduser("~/playwright_profile")

def human_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))

with sync_playwright() as p:
    # Utiliser launch_persistent_context pour ouvrir un navigateur "local" avec profil
    # headless=False pour voir la fenêtre locale
    browser_context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False,  # visible : utile pour utiliser le navigateur local
        args=["--disable-blink-features=AutomationControlled"],
        viewport={"width": 1280, "height": 720},
        locale="fr-FR",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )

    page = browser_context.new_page()

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

        # ✍️ Email (écriture humaine simulée)
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

        # 🧠 DEBUG boutons
        buttons = page.locator("button, input[type='submit']")
        try:
            count = buttons.count()
        except Exception:
            count = 0
        print("Nombre de boutons trouvés :", count)

        for i in range(count):
            try:
                txt = buttons.nth(i).inner_text().strip()
                print(f"Bouton {i+1} texte : {txt}")
            except Exception:
                try:
                    val = buttons.nth(i).get_attribute("value") or ""
                    print(f"Bouton {i+1} value : {val}")
                except Exception:
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

        # 🔥 2. CLIQUER LOGIN
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

        print("Résultat login :", login_clicked)

        # ⏳ Attente après login (fixe)
        print("Attente fixe de 7 secondes après le clic login...")
        time.sleep(7)

        print("Après login URL :", page.url)

        # Si vous voulez sauvegarder l'état de la session (cookies/localStorage) pour réutiliser plus tard :
        try:
            storage_path = os.path.join(USER_DATA_DIR, "storageState.json")
            browser_context.storage_state(path=storage_path)
            print("Storage state sauvegardé dans :", storage_path)
        except Exception as e:
            print("Impossible de sauvegarder storage state :", e)

    except Exception as e:
        print("Erreur :", e)

    finally:
        # Ne pas fermer le navigateur automatiquement si vous voulez l'utiliser localement après le script.
        # Si vous voulez qu'il reste ouvert pour inspection, commentez la ligne suivante.
        browser_context.close()

print("Bot terminé")
