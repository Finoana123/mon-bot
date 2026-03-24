import random
import time
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
USE_STORED_SESSION = False  # True pour réutiliser storageState.json
STORAGE_FILE = "storageState.json"

def human_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))

with sync_playwright() as p:
    # Mode visible pour debug ; en production vous pouvez repasser headless=True
    browser = p.chromium.launch(headless=False, slow_mo=100)

    context_args = {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "viewport": {"width": 1280, "height": 720},
        "locale": "fr-FR",
        # "proxy": {"server": "http://user:pass@proxy:port"}  # décommentez si vous utilisez un proxy
    }

    if USE_STORED_SESSION and os.path.exists(STORAGE_FILE):
        context = browser.new_context(storage_state=STORAGE_FILE, **context_args)
    else:
        context = browser.new_context(**context_args)

    page = context.new_page()

    try:
        page.goto("https://tronpick.io/login.php", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        human_delay(2,4)

        print("URL :", page.url)
        print("Titre :", page.title())

        # Remplir email/password si pas de session stockée
        if not (USE_STORED_SESSION and os.path.exists(STORAGE_FILE)):
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
            human_delay(1,2)

        # Debug : lister boutons
        buttons = page.locator("button, input[type='submit']")
        count = buttons.count()
        print("Nombre de boutons trouvés :", count)
        for i in range(count):
            try:
                print(f"Bouton {i+1} texte :", buttons.nth(i).inner_text().strip())
            except:
                print(f"Bouton {i+1} sans texte")

        # Cliquer le bouton numéro 2 (index 1) en s'assurant que ce n'est pas "verify"
        target_idx = 1
        if target_idx < count:
            text = (buttons.nth(target_idx).inner_text() or buttons.nth(target_idx).get_attribute("value") or "").lower().strip()
            if "verify" in text:
                print("Le bouton cible contient 'verify' — on n'exécute pas le clic.")
            else:
                print(f"Clique sur le bouton index {target_idx} texte: {text}")
                buttons.nth(target_idx).click()
                human_delay(1,2)
        else:
            print("Index cible hors plage des boutons")

        # Cliquer login et attendre navigation correctement
        # On utilise locator pour trouver le bouton login précisément
        login_locator = page.locator("button, input[type='submit']").filter(has_text="Log in")
        if login_locator.count() == 0:
            # fallback : chercher par texte partiel
            login_locator = page.locator("button, input[type='submit']").filter(has_text="login")
        if login_locator.count() > 0:
            print("Tentative de clic sur login...")
            with page.expect_navigation(timeout=20000, wait_until="networkidle"):
                login_locator.nth(0).click()
            human_delay(7,7)  # attente fixe de 7s demandée
        else:
            print("Bouton login non trouvé par locator; tentative d'évaluation JS")
            page.evaluate("""
                () => {
                    const btns = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                    for (let b of btns) {
                        const t = (b.innerText || b.value || '').toLowerCase();
                        if (t.includes('login') || t.includes('log in') || t.includes('sign in')) {
                            b.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)
            human_delay(7,7)

        print("URL après tentative login :", page.url)

        # Si connexion réussie, sauvegarder storageState pour réutiliser la session
        if "login.php" not in page.url and not USE_STORED_SESSION:
            print("Connexion détectée — sauvegarde de la session dans", STORAGE_FILE)
            context.storage_state(path=STORAGE_FILE)

        # Si toujours sur login, tenter d'ouvrir faucet (mais si site exige session, cela retournera login)
        if "faucet.php" not in page.url:
            print("Tentative d'accès direct à /faucet.php ...")
            page.goto("https://tronpick.io/faucet.php", timeout=20000)
            page.wait_for_load_state("domcontentloaded")
            print("Après goto faucet URL :", page.url)

        # Fin des actions
    except Exception as e:
        print("Erreur :", e)
    finally:
        context.close()
        browser.close()
