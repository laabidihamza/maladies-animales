import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
import langdetect
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')

class SeleniumAnimalDiseaseNewsScraper:
    def __init__(self, input_csv: str, headless: bool = True):
        """
        Initialise le scraper Selenium avec le fichier CSV contenant les URLs
        
        Args:
            input_csv: Chemin vers le fichier CSV avec colonnes 'code' et 'lien'
            headless: Si True, le navigateur s'exécute en arrière-plan (sans interface)
        """
        self.input_csv = input_csv
        self.df_urls = pd.read_csv(input_csv)
        self.results = []
        self.headless = headless
        self.driver = None
        
        # Mots-clés pour identifier la source
        self.social_media = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube']
        self.official_sources = ['gov', 'who', 'oie', 'fao', 'ministere', 'ministry', 'gouvernement']
    
    def setup_driver(self):
        """Configure et initialise le driver Selenium Chrome"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Options pour améliorer la performance et éviter la détection
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Désactiver les notifications et popups
        prefs = {
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_settings.popups': 0,
        }
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            print("Driver Selenium initialisé avec succès")
        except Exception as e:
            print(f"Erreur lors de l'initialisation du driver: {e}")
            print("Assurez-vous que ChromeDriver est installé et dans le PATH")
            raise
    
    def close_driver(self):
        """Ferme le driver Selenium"""
        if self.driver:
            self.driver.quit()
            print("Driver fermé")
    
    def detect_language(self, text: str) -> str:
        """Détecte la langue du texte"""
        try:
            lang_code = langdetect.detect(text)
            lang_map = {
                'ar': 'arabe',
                'fr': 'français',
                'en': 'anglais',
                'es': 'espagnol',
                'de': 'allemand'
            }
            return lang_map.get(lang_code, lang_code)
        except:
            return 'non détecté'
    
    def extract_date(self, driver, soup: BeautifulSoup, text: str) -> str:
        """Extrait la date de publication"""
        # Chercher dans les balises meta
        date_patterns = [
            {'property': 'article:published_time'},
            {'name': 'publishdate'},
            {'name': 'date'},
            {'itemprop': 'datePublished'}
        ]
        
        for pattern in date_patterns:
            meta_tag = soup.find('meta', pattern)
            if meta_tag and meta_tag.get('content'):
                date_str = meta_tag['content']
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    return date_obj.strftime('%d-%m-%Y')
                except:
                    pass
        
        # Chercher avec Selenium les éléments time
        try:
            time_elements = driver.find_elements(By.TAG_NAME, 'time')
            for time_elem in time_elements:
                datetime_attr = time_elem.get_attribute('datetime')
                if datetime_attr:
                    try:
                        date_obj = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                        return date_obj.strftime('%d-%m-%Y')
                    except:
                        pass
        except:
            pass
        
        # Pattern regex pour dates dans le texte
        date_regex = r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b'
        matches = re.findall(date_regex, text[:500])
        if matches:
            return matches[0]
        
        return 'non trouvé'
    
    def extract_location(self, text: str) -> str:
        """Extrait le lieu mentionné dans la news"""
        locations = ['Tunisie', 'France', 'Maroc', 'Algérie', 'Egypte', 'Tunisia', 
                    'Morocco', 'Algeria', 'Egypt', 'Tunis', 'Paris', 'Rabat',
                    'Casablanca', 'Alger', 'Le Caire', 'Sfax', 'Sousse']
        
        for location in locations:
            if location.lower() in text.lower():
                return location
        
        return 'non spécifié'
    
    def extract_disease(self, text: str) -> str:
        """Extrait le nom de la maladie"""
        diseases = [
            'grippe aviaire', 'fièvre aphteuse', 'peste porcine', 'rage',
            'brucellose', 'tuberculose', 'anthrax', 'salmonellose',
            'avian flu', 'foot and mouth', 'rabies', 'covid', 'monkeypox',
            'الحمى القلاعية', 'أنفلونزا الطيور', 'داء الكلب',
            'peste bovine', 'charbon', 'listériose', 'campylobacter'
        ]
        
        text_lower = text.lower()
        for disease in diseases:
            if disease.lower() in text_lower:
                return disease
        
        return 'non identifié'
    
    def classify_source(self, url: str) -> str:
        """Classe la source de publication"""
        url_lower = url.lower()
        
        # Vérifier réseaux sociaux
        for social in self.social_media:
            if social in url_lower:
                return f'réseaux sociaux ({social.capitalize()})'
        
        # Vérifier sites officiels
        for official in self.official_sources:
            if official in url_lower:
                return 'site officiel'
        
        # Vérifier médias
        media_keywords = ['news', 'journal', 'radio', 'tv', 'media', 'presse', 'info']
        for keyword in media_keywords:
            if keyword in url_lower:
                return 'médias'
        
        return 'autre'
    
    def generate_summary(self, text: str, word_count: int) -> str:
        """Génère un résumé de longueur spécifiée"""
        words = text.split()
        if len(words) <= word_count:
            return text
        
        summary = ' '.join(words[:word_count])
        
        # Essayer de terminer à une phrase complète
        last_period = summary.rfind('.')
        if last_period > word_count * 0.7 * 5:
            summary = summary[:last_period + 1]
        else:
            summary += '...'
        
        return summary.strip()
    
    def extract_named_entities(self, text: str) -> str:
        """Extrait les entités nommées (organismes, animaux, etc.)"""
        entities = []
        
        # Organismes
        organizations = ['OMS', 'WHO', 'FAO', 'OIE', 'WOAH', 'ministère', 'ministry', 
                        'université', 'university', 'institut', 'centre', 'laboratoire']
        
        # Animaux
        animals = ['bovins', 'volailles', 'porcs', 'ovins', 'caprins',
                  'cattle', 'poultry', 'pigs', 'sheep', 'goats',
                  'poulet', 'vache', 'mouton', 'chèvre', 'cheval',
                  'chicken', 'cow', 'horse', 'أبقار', 'دواجن']
        
        text_lower = text.lower()
        
        for org in organizations:
            if org.lower() in text_lower:
                pattern = rf'\b[\w\s]{{0,20}}{re.escape(org)}[\w\s]{{0,20}}\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    entities.extend(matches[:2])
        
        for animal in animals:
            if animal.lower() in text_lower:
                entities.append(animal)
        
        return '; '.join(set([e.strip() for e in entities])) if entities else 'aucune'
    
    def wait_for_page_load(self, driver, timeout: int = 10):
        """Attend que la page soit complètement chargée"""
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(2)  # Attendre les éléments JavaScript dynamiques
        except TimeoutException:
            print("Timeout en attendant le chargement de la page")
    
    def scrape_url(self, code: str, url: str) -> Dict:
        """Scrape une URL avec Selenium et extrait toutes les informations"""
        print(f"Scraping: {code} - {url}")
        
        result = {
            'code': code,
            'url': url,
            'titre': '',
            'contenu': '',
            'langue': '',
            'nb_caracteres': 0,
            'nb_mots': 0,
            'date_publication': '',
            'lieu': '',
            'maladie': '',
            'source': '',
            'resume_50': '',
            'resume_100': '',
            'resume_150': '',
            'entites_nommees': '',
            'status': 'échec'
        }
        
        try:
            # Charger la page
            self.driver.get(url)
            self.wait_for_page_load(self.driver)
            
            # Scroller pour charger le contenu dynamique
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            
            # Récupérer le HTML de la page
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Supprimer scripts et styles
            for script in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe']):
                script.decompose()
            
            # Extraire le titre
            title = ''
            try:
                # Essayer avec Selenium d'abord
                title_elem = self.driver.find_element(By.TAG_NAME, 'h1')
                title = title_elem.text.strip()
            except:
                # Fallback avec BeautifulSoup
                title_tag = soup.find('h1') or soup.find('title')
                title = title_tag.text.strip() if title_tag else 'non trouvé'
            
            result['titre'] = title
            
            # Extraire le contenu
            content = ''
            
            # Essayer différents sélecteurs avec Selenium
            content_selectors = [
                (By.TAG_NAME, 'article'),
                (By.TAG_NAME, 'main'),
                (By.CLASS_NAME, 'content'),
                (By.CLASS_NAME, 'article-body'),
                (By.CLASS_NAME, 'post-content'),
                (By.ID, 'content'),
            ]
            
            for by, selector in content_selectors:
                try:
                    content_elem = self.driver.find_element(by, selector)
                    content = content_elem.text.strip()
                    if content and len(content) > 100:
                        break
                except:
                    continue
            
            # Fallback avec BeautifulSoup si Selenium n'a rien trouvé
            if not content or len(content) < 100:
                body = soup.find('body')
                content = body.get_text(separator=' ', strip=True) if body else ''
            
            # Nettoyer le contenu
            content = re.sub(r'\s+', ' ', content).strip()
            result['contenu'] = content
            
            # Calculer statistiques
            result['nb_caracteres'] = len(content)
            result['nb_mots'] = len(content.split())
            
            # Extraire les autres informations
            result['langue'] = self.detect_language(content[:500])
            result['date_publication'] = self.extract_date(self.driver, soup, content)
            result['lieu'] = self.extract_location(content)
            result['maladie'] = self.extract_disease(content)
            result['source'] = self.classify_source(url)
            
            # Générer les résumés
            result['resume_50'] = self.generate_summary(content, 50)
            result['resume_100'] = self.generate_summary(content, 100)
            result['resume_150'] = self.generate_summary(content, 150)
            
            # Extraire entités nommées
            result['entites_nommees'] = self.extract_named_entities(content)
            
            result['status'] = 'succès'
            
        except TimeoutException:
            print(f"Timeout pour {url}")
            result['status'] = 'erreur: timeout'
        
        except WebDriverException as e:
            print(f"Erreur WebDriver pour {url}: {str(e)[:100]}")
            result['status'] = f'erreur: {str(e)[:50]}'
        
        except Exception as e:
            print(f"Erreur inattendue pour {url}: {str(e)}")
            result['status'] = f'erreur: {str(e)[:50]}'
        
        return result
    
    def scrape_all(self, delay: float = 3.0) -> pd.DataFrame:
        """Scrape toutes les URLs du fichier CSV"""
        print(f"Début du scraping de {len(self.df_urls)} URLs avec Selenium...")
        
        # Initialiser le driver
        self.setup_driver()
        
        try:
            for idx, row in self.df_urls.iterrows():
                code = row['code']
                url = row['lien']
                
                result = self.scrape_url(code, url)
                self.results.append(result)
                
                # Délai entre les requêtes
                time.sleep(delay)
                
                # Sauvegarde intermédiaire tous les 10 URLs
                if (idx + 1) % 10 == 0:
                    self.save_results(f'resultats_selenium_intermediaires_{idx+1}.csv')
                    print(f"Progression: {idx+1}/{len(self.df_urls)} URLs traitées")
        
        finally:
            # Toujours fermer le driver
            self.close_driver()
        
        print("Scraping terminé!")
        return pd.DataFrame(self.results)
    
    def save_results(self, output_file: str = 'dataset_maladies_animales_selenium.csv'):
        """Sauvegarde les résultats dans un fichier CSV"""
        df_results = pd.DataFrame(self.results)
        df_results.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Résultats sauvegardés dans: {output_file}")
        return df_results


# Exemple d'utilisation
if __name__ == "__main__":
    # Option 1: Spécifier directement le chemin
    input_file = 'urls.csv'  # MODIFIEZ CE CHEMIN
    
    # Option 2: Demander à l'utilisateur (décommentez les 2 lignes ci-dessous)
    # print("Entrez le chemin du fichier CSV contenant les URLs:")
    # input_file = input().strip()
    
    # Créer le scraper (headless=False pour voir le navigateur, True pour arrière-plan)
    scraper = SeleniumAnimalDiseaseNewsScraper(input_file, headless=True)
    
    # Scraper toutes les URLs
    df_results = scraper.scrape_all(delay=3.0)
    
    # Sauvegarder les résultats finaux
    output_file = 'dataset_maladies_animales_selenium_final.csv'  # MODIFIEZ SI NÉCESSAIRE
    scraper.save_results(output_file)
    
    # Afficher un résumé
    print("\n=== RÉSUMÉ DU SCRAPING ===")
    print(f"Total URLs traitées: {len(df_results)}")
    print(f"Succès: {len(df_results[df_results['status'] == 'succès'])}")
    print(f"Échecs: {len(df_results[df_results['status'] != 'succès'])}")
    print("\nDistribution des langues:")
    print(df_results['langue'].value_counts())
    print("\nDistribution des sources:")
    print(df_results['source'].value_counts())