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

# Adresse du proxy fournie par l'utilisateur
PROXY_SERVER = "http://84.8.134.235:8888"

with sync_playwright() as p:
    # NOTE: pour debug visuel, mettez headless=False et slow_mo=100
    try:
        browser = p.chromium.launch(
            headless=False,  # passez à True en production
            slow_mo=50,
            proxy={"server": PROXY_SERVER},
            args=["--disable-blink-features=AutomationControlled"]
        )
    except Exception as e:
        print("Erreur lors du lancement du navigateur avec proxy :", e)
        print("Essai de lancement sans proxy en secours...")
        browser = p.chromium.launch(headless=False, slow_mo=50, args=["--disable-blink-features=AutomationControlled"])

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        viewport={"width": 1280, "height": 720},
        locale="fr-FR"
    )

    page = context.new_page()

    try:
        # ---------------------------
        # Test de connectivité via le proxy (page fournie)
        try:
            print("Tentative d'accès au test proxy :", PROXY_SERVER)
            page.goto("http://84.8.134.235:8888/", timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            print("Test proxy - URL atteinte :", page.url)
            # Afficher un extrait du contenu pour debug (limité)
            try:
                snippet = page.locator("body").inner_text()[:200]
                print("Contenu body (début) :", snippet)
            except Exception:
                print("Impossible de lire le contenu body du test proxy.")
        except Exception as e:
            print("Échec du test proxy :", e)
            # On continue quand même pour tenter d'accéder au site cible (peut échouer si proxy requis)
        
        # ---------------------------
        # Aller sur login
        page.goto("https://tronpick.io/login.php", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        human_delay(3,5)

        print("URL :", page.url)
        print("Titre :", page.title())

        # Refresh page (important)
        page.reload()
        human_delay(3,5)

        # Sélecteurs
        email_selector = "input[type='email'], input[name='email'], input[placeholder*='mail']"
        password_selector = "input[type='password']"

        page.wait_for_selector(email_selector, timeout=60000)

        # Remplir email
        page.click(email_selector)
        for c in EMAIL:
            page.keyboard.type(c)
            time.sleep(random.uniform(0.05, 0.15))

        human_delay(1,3)

        # Remplir password
        page.click(password_selector)
        for c in PASSWORD:
            page.keyboard.type(c)
            time.sleep(random.uniform(0.05, 0.15))

        # Attente humaine aléatoire
        wait_time = random.uniform(5, 10)
        print(f"Attente avant actions : {wait_time:.2f} secondes")
        time.sleep(wait_time)

        # Debug boutons
        buttons = page.locator("button, input[type='submit']")
        count = buttons.count()
        print("Nombre de boutons trouvés :", count)
        for i in range(count):
            try:
                txt = buttons.nth(i).inner_text().strip()
                print(f"Bouton {i+1} texte : {txt}")
            except Exception:
                try:
                    val = buttons.nth(i).get_attribute("value") or ""
                    print(f"Bouton {i+1} value : {val}")
                except:
                    print(f"Bouton {i+1} sans texte")

        # Mouvement souris
        page.mouse.move(400, 400)
        human_delay(1,2)

        # Clic ciblé : bouton numéro 2 (numérotation humaine -> index 1)
        target_idx = 1
        if target_idx < count:
            # Vérifier que ce n'est pas un bouton "Verify"
            try:
                t = (buttons.nth(target_idx).inner_text() or buttons.nth(target_idx).get_attribute("value") or "").lower().strip()
            except Exception:
                t = ""
            if "verify" in t:
                print("Le bouton cible contient 'verify' — on ne clique pas dessus.")
            else:
                print(f"Clique sur le bouton index {target_idx+1} (0-based {target_idx}) texte/value: {t}")
                try:
                    buttons.nth(target_idx).click()
                except Exception as e:
                    print("Erreur lors du clic par locator :", e)
        else:
            print("Index cible hors plage des boutons trouvés.")

        human_delay(1,2)

        # Cliquer login et attendre 7 secondes après le clic
        # On cherche le bouton login par texte (cas-insensible)
        login_locator = page.locator("button, input[type='submit']").filter(has_text="Log in")
        if login_locator.count() == 0:
            login_locator = page.locator("button, input[type='submit']").filter(has_text="login")
        if login_locator.count() > 0:
            print("Tentative de clic sur login via locator...")
            try:
                # on ne bloque pas indéfiniment : on clique puis on attend 7s comme demandé
                login_locator.nth(0).click()
                print("Login cliqué, attente fixe de 7 secondes...")
                time.sleep(7)
            except Exception as e:
                print("Erreur lors du clic login via locator :", e)
        else:
            # fallback JS si locator n'a rien trouvé
            print("Bouton login non trouvé par locator, tentative via JS evaluate...")
            res = page.evaluate("""
            () => {
                const btns = Array.from(document.querySelectorAll('button, input[type=\"submit\"]'));
                for (let b of btns) {
                    const t = (b.innerText || b.value || '').toLowerCase();
                    if (t.includes('login') || t.includes('log in') || t.includes('sign in')) {
                        try { b.click(); return 'clicked via js'; } catch(e) { return 'click error: ' + e.toString(); }
                    }
                }
                return 'login not found';
            }
            """)
            print("Résultat evaluate login :", res)
            print("Attente fixe de 7 secondes après evaluate...")
            time.sleep(7)

        # Vérifier navigation / session
        try:
            current_url = page.url
        except Exception:
            current_url = "inconnue"
        print("URL actuelle après login :", current_url)

        # Si on n'est pas connecté, tenter d'ouvrir faucet.php (mais si session non valide, redirection vers login se produira)
        if "faucet.php" not in current_url:
            print("Tentative d'accès direct à /faucet.php ...")
            try:
                page.goto("https://tronpick.io/faucet.php", timeout=20000)
                page.wait_for_load_state("domcontentloaded", timeout=15000)
                print("Après goto faucet URL :", page.url)
            except Exception as e:
                print("Impossible d'ouvrir faucet.php directement :", e)

    except Exception as e:
        print("Erreur générale :", e)

    finally:
        try:
            context.close()
        except:
            pass
        browser.close()

print("Bot terminé")
