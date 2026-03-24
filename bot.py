import os
import sys
import time
import random
import traceback
import requests
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

def test_proxy_http(proxy_url, test_url=None, timeout=8):
    if test_url is None:
        test_url = proxy_url
    try:
        print(f"[proxy test] GET {test_url} via {proxy_url}")
        r = requests.get(test_url, timeout=timeout)
        print("[proxy test] status:", r.status_code)
        return True
    except Exception as e:
        print("[proxy test] échec:", repr(e))
        return False

def ensure_env_vars():
    if not EMAIL or not PASSWORD:
        print("Erreur : EMAIL ou PASSWORD manquant !")
        sys.exit(1)

# ---------------------------
# Script principal
# ---------------------------
def main():
    ensure_env_vars()

    # 1) Test proxy simple via requests pour détecter connectivité
    proxy_ok = test_proxy_http(PROXY_SERVER)
    if not proxy_ok:
        print("Attention : test proxy échoué. Le runner peut ne pas atteindre le proxy.")
        # On continue quand même pour tenter d'exécuter Playwright (selon votre besoin)
        # sys.exit(1)

    try:
        with sync_playwright() as p:
            # 2) Lancer le navigateur avec proxy
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
                # 3) Test rapide d'accès au proxy via Playwright (page fournie)
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
                    print("[test] échec test proxy via Playwright:", e)
                    # on continue

                # 4) Aller sur la page de login
                print("[flow] navigation vers https://tronpick.io/login.php")
                page.goto("https://tronpick.io/login.php", timeout=60000)
                page.wait_for_load_state("domcontentloaded")
                human_delay(2,4)
                print("[flow] URL :", page.url)
                print("[flow] Titre :", page.title())

                # 5) Refresh (comme dans votre logique)
                page.reload()
                human_delay(2,4)

                # 6) Remplir email/password
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

                # 7) Attente humaine aléatoire
                wait_time = random.uniform(5, 10)
                print(f"[flow] attente avant actions : {wait_time:.2f} secondes")
                time.sleep(wait_time)

                # 8) Lister boutons pour debug
                buttons = page.locator("button, input[type='submit']")
                try:
                    count = buttons.count()
                except Exception:
                    count = 0
                print("[debug] Nombre de boutons trouvés :", count)
                for i in range(count):
                    try:
                        txt = buttons.nth(i).inner_text().strip()
                        print(f"[debug] Bouton {i+1} texte : {txt}")
                    except Exception:
                        try:
                            val = buttons.nth(i).get_attribute("value") or ""
                            print(f"[debug] Bouton {i+1} value : {val}")
                        except Exception:
                            print(f"[debug] Bouton {i+1} sans texte")

                # 9) Cliquer le bouton numéro 2 (numérotation humaine -> index 1)
                target_idx = 1
                if target_idx < count:
                    try:
                        t = (buttons.nth(target_idx).inner_text() or buttons.nth(target_idx).get_attribute("value") or "").lower().strip()
                    except Exception:
                        t = ""
                    if "verify" in t:
                        print("[action] le bouton cible contient 'verify' — on ne clique pas dessus.")
                    else:
                        print(f"[action] clic sur bouton numéro {target_idx+1} (index {target_idx}) texte/value: {t}")
                        try:
                            buttons.nth(target_idx).click()
                        except Exception as e:
                            print("[action] erreur lors du clic par locator:", e)
                else:
                    print("[action] index cible hors plage des boutons trouvés.")

                human_delay(1,2)

                # 10) Cliquer login et attendre exactement 7 secondes après le clic
                # Recherche du bouton login par texte (cas-insensible)
                login_locator = page.locator("button, input[type='submit']").filter(has_text="Log in")
                if login_locator.count() == 0:
                    login_locator = page.locator("button, input[type='submit']").filter(has_text="login")
                if login_locator.count() > 0:
                    print("[action] tentative de clic sur login via locator...")
                    try:
                        login_locator.nth(0).click()
                        print("[action] login cliqué, attente fixe de 7 secondes...")
                        time.sleep(7)
                    except Exception as e:
                        print("[action] erreur lors du clic login via locator:", e)
                        print("[action] tentative via JS evaluate...")
                        res = page.evaluate("""
                            () => {
                                const btns = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                                for (let b of btns) {
                                    const t = (b.innerText || b.value || '').toLowerCase();
                                    if (t.includes('login') || t.includes('log in') || t.includes('sign in')) {
                                        try { b.click(); return 'clicked via js'; } catch(e) { return 'click error: ' + e.toString(); }
                                    }
                                }
                                return 'login not found';
                            }
                        """)
                        print("[action] résultat evaluate login :", res)
                        print("[action] attente fixe de 7 secondes après evaluate...")
                        time.sleep(7)
                else:
                    print("[action] bouton login non trouvé par locator, tentative via JS evaluate...")
                    res = page.evaluate("""
                        () => {
                            const btns = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                            for (let b of btns) {
                                const t = (b.innerText || b.value || '').toLowerCase();
                                if (t.includes('login') || t.includes('log in') || t.includes('sign in')) {
                                    try { b.click(); return 'clicked via js'; } catch(e) { return 'click error: ' + e.toString(); }
                                }
                            }
                            return 'login not found';
                        }
                    """)
                    print("[action] résultat evaluate login :", res)
                    print("[action] attente fixe de 7 secondes après evaluate...")
                    time.sleep(7)

                # 11) Vérifier URL / session
                try:
                    current_url = page.url
                except Exception:
                    current_url = "inconnue"
                print("[flow] URL actuelle après login :", current_url)

                # 12) Si pas sur faucet.php, tenter d'y aller directement
                if "faucet.php" not in current_url:
                    print("[fallback] tentative d'accès direct à /faucet.php ...")
                    try:
                        page.goto("https://tronpick.io/faucet.php", timeout=20000)
                        page.wait_for_load_state("domcontentloaded", timeout=15000)
                        print("[fallback] Après goto faucet URL :", page.url)
                    except Exception as e:
                        print("[fallback] impossible d'ouvrir faucet.php directement :", e)

                # 13) Si connexion détectée, sauvegarder storageState (optionnel)
                if "login.php" not in current_url:
                    try:
                        print("[session] connexion détectée, sauvegarde storageState dans", STORAGE_FILE)
                        context.storage_state(path=STORAGE_FILE)
                    except Exception as e:
                        print("[session] impossible de sauvegarder storageState:", e)

            except Exception as inner_e:
                print("[flow] exception interne:")
                traceback.print_exc()
                raise inner_e
            finally:
                try:
                    context.close()
                except Exception:
                    pass
                browser.close()

    except Exception as e:
        print("[erreur globale] exception attrapée:")
        traceback.print_exc()
        # sortir avec code d'erreur pour CI
        sys.exit(1)

if __name__ == "__main__":
    main()
