from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import logging

# Configurer le logging
logging.basicConfig(level=logging.INFO)

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--lang=fr")
    return webdriver.Chrome(options=options)

def extract_article_data(driver, url):
    try:
        driver.get(url)
        time.sleep(2)  # Attente basique

        # Titre : essayer plusieurs balises
        title = None
        for selector in ["h1", "title", "header h1", ".article-title", ".post-title"]:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                title = elem.text.strip()
                if title:
                    break
            except:
                continue

        # Contenu : essayer des sélecteurs génériques
        content = ""
        for selector in ["article", ".article-content", ".post-content", "main", "body"]:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                content = elem.text.strip()
                if content:
                    break
            except:
                continue

        # Si échec, récupérer tout le body
        if not content:
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                content = body.text.strip()
            except:
                content = ""

        return {
            "url": url,
            "titre": title or "Titre non trouvé",
            "contenu": content or "Contenu non récupéré",
        }

    except Exception as e:
        logging.error(f"Erreur pour {url}: {str(e)}")
        return {
            "url": url,
            "titre": "Erreur",
            "contenu": "Erreur lors du scraping"
        }