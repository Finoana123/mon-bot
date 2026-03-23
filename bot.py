#!/usr/bin/env python3
import os
import time
import random
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

# -------------------------
# Configuration
# -------------------------
# Définir HEADLESS et SLOW_MO via variables d'environnement si besoin
HEADLESS = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")
SLOW_MO = int(os.getenv("SLOW_MO", "0"))  # ms, 0 = none
SCREENSHOT_DIR = Path(os.getenv("SCREENSHOT_DIR", "."))

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# -------------------------
# Utilitaires
# -------------------------
def human_delay(a=0.5, b=1.5):
    time.sleep(random.uniform(a, b))

def type_like_human(page, selector, text, min_delay=0.05, max_delay=0.15):
    """Clique sur le champ et tape caractère par caractère."""
    page.click(selector)
    for ch in text:
        page.keyboard.type(ch)
        time.sleep(random.uniform(min_delay, max_delay))

def ensure_dir(d: Path):
    if not d.exists():
        d.mkdir(parents=True, exist_ok=True)

def save_debug(page, name_prefix="debug"):
    ensure_dir(SCREENSHOT_DIR)
    ts = int(time.time())
    png = SCREENSHOT_DIR / f"{name_prefix}_{ts}.png"
    html = SCREENSHOT_DIR / f"{name_prefix}_{ts}.html"
    try:
        page.screenshot(path=str(png), full_page=True)
    except Exception:
        pass
    try:
        with open(html, "w", encoding="utf-8") as f:
            f.write(page.content())
    except Exception:
        pass
    return str(png), str(html)

def find_button_in_frames(page, selector):
    """Retourne (frame, locator) si trouvé dans une frame ou page principale."""
    # Cherche dans la page principale
    locator = page.locator(selector)
    if locator.count() > 0:
        return page, locator
    # Cherche dans les frames
    for frame in page.frames:
        try:
            loc = frame.locator(selector)
            if loc.count() > 0:
                return frame, loc
        except Exception:
            continue
    return None, None

def robust_click(page, selector, max_retries=3, base_timeout=15000):
    """
    Tentative robuste de clic :
    - attend visible
    - click normal
    - click force
    - fallback JS click
    - retries avec backoff
    Retourne True si succès, False sinon.
    """
    attempt = 0
    while attempt < max_retries:
        attempt += 1
        try:
            frame_or_page, locator = find_button_in_frames(page, selector)
            if not locator:
                raise Exception(f"No locator matches selector: {selector}")

            # Utiliser le premier élément trouvé
            loc = locator.first

            # Attendre visible et enabled
            loc.wait_for(state="visible", timeout=base_timeout)
            if not loc.is_enabled():
                # attendre un peu si disabled
                time.sleep(0.5)

            # Scroll into view then try click
            loc.scroll_into_view_if_needed()
            loc.click(timeout=base_timeout)
            return True
        except PWTimeoutError as te:
            # Timeout waiting for visible/clickable
            try:
                # Essayer click forcé
                if locator:
                    locator.first.click(force=True, timeout=5000)
                    return True
            except Exception:
                pass
            # JS fallback
            try:
                page.evaluate(
                    """(sel) => {
                        const el = document.querySelector(sel);
                        if (!el) return false;
                        el.scrollIntoView({block: 'center'});
                        el.click();
                        return true;
                    }""",
                    selector,
                )
                return True
            except Exception:
                pass
            # sauvegarde debug
            try:
                save_debug(page, name_prefix=f"click_timeout_attempt{attempt}")
            except Exception:
                pass
            # backoff
            time.sleep(1.5 ** attempt)
        except Exception as e:
            # Dernier recours : JS fallback global (tente sur frames aussi)
            try:
                page.evaluate(
                    """(sel) => {
                        const el = document.querySelector(sel);
                        if (el) { el.scrollIntoView({block:'center'}); el.click(); return true; }
                        // try all frames
                        for (const f of window.frames) {
                            try {
                                const doc = f.document;
                                const e2 = doc.querySelector(sel);
                                if (e2) { e2.scrollIntoView({block:'center'}); e2.click(); return true; }
                            } catch (err) {}
                        }
                        return false;
                    }""",
                    selector,
                )
                return True
            except Exception:
                save_debug(page, name_prefix=f"click_error_attempt{attempt}")
                time.sleep(1.5 ** attempt)
    return False

# -------------------------
# Script principal
# -------------------------
def main():
    print("Bot PRO démarré")

    if not EMAIL or not PASSWORD:
        print("ERROR: EMAIL and PASSWORD environment variables must be set. Aborting.")
        return

    ensure_dir(SCREENSHOT_DIR)

    with sync_playwright() as p:
        browser = None
        context = None
        page = None
        try:
            browser = p.chromium.launch(
                headless=HEADLESS,
                slow_mo=SLOW_MO,
                args=["--disable-blink-features=AutomationControlled"]
            )

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                locale="fr-FR"
            )

            page = context.new_page()
            page.set_default_timeout(60000)

            # Aller sur la page de login
            page.goto("https://tronpick.io/login.php", timeout=60000)
            page.wait_for_load_state("domcontentloaded")
            human_delay(2, 4)

            print("URL :", page.url)
            print("Titre :", page.title())

            # Sélecteurs
            email_selector = "input[type='email'], input[name='email'], input[placeholder*='mail']"
            password_selector = "input[type='password']"
            submit_selector = "button[type='submit'], button:has-text('Login'), input[type='submit']"

            # Attendre champs
            try:
                page.wait_for_selector(email_selector, timeout=20000)
                page.wait_for_selector(password_selector, timeout=20000)
            except PWTimeoutError:
                print("Les champs email/password n'ont pas été trouvés dans le délai.")
                save_debug(page, "missing_fields")
                return

            # Remplissage
            type_like_human(page, email_selector, EMAIL)
            human_delay(0.5, 1.2)
            type_like_human(page, password_selector, PASSWORD)
            human_delay(1.5, 3.0)

            # Petit mouvement souris
            try:
                page.mouse.move(400, 400)
            except Exception:
                pass
            human_delay(0.5, 1.2)

            # Essayer clic robuste
            clicked = robust_click(page, submit_selector, max_retries=4, base_timeout=20000)
            if not clicked:
                print("Échec du clic sur le bouton de connexion après plusieurs tentatives.")
                save_debug(page, "login_click_failed")
                return

            # Attendre navigation ou changement d'URL
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
            except Exception:
                # networkidle peut échouer; attendre un peu et vérifier URL
                human_delay(2, 4)

            print("Après login URL :", page.url)
            # Optionnel: vérifier présence d'un élément indiquant succès
            # ex: page.locator("selector_after_login").wait_for(...)

        except Exception as e:
            print("Erreur inattendue :", str(e))
            if page:
                png, html = save_debug(page, "exception")
                print("Debug saved:", png, html)
            # afficher trace pour debug (sans exposer mot de passe)
            traceback.print_exc()
        finally:
            try:
                if context:
                    context.close()
            except Exception:
                pass
            try:
                if browser:
                    browser.close()
            except Exception:
                pass

    print("Bot terminé")

if __name__ == "__main__":
    main()
