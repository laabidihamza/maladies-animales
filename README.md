# 🐾 Projet Web Scraping - Maladies Animales

Système automatisé d'extraction et d'analyse de news sur les maladies animales avec Selenium et LLM.

## 📋 Description

Ce projet extrait automatiquement des informations à partir d'URLs de news sur les maladies animales et génère un dataset CSV structuré avec :
- Métadonnées (titre, langue, dates, lieux)
- Analyse de contenu (maladie, animal concerné)
- Résumés automatiques (50, 100, 150 mots)

## 🏗️ Architecture

```
animal_disease_scraper/
├── data/
│   ├── input/           # Fichier URLs d'entrée
│   ├── output/          # Résultats (CSV)
│   └── logs/            # Logs d'exécution
├── src/
│   ├── scraper.py       # Module Selenium
│   ├── llm_analyzer.py  # Module LLM
│   ├── utils.py         # Utilitaires
│   └── config.py        # Configuration
└── main.py              # Script principal
```

## 🚀 Installation

### 1. Prérequis
```bash
# Python 3.8+
python --version

# Chrome/Chromium installé sur votre système
```

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 3. Installation d'Ollama (LLM local gratuit)

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

**Windows:**
- Télécharger depuis https://ollama.com/download
- Installer et exécuter
- Ouvrir terminal: `ollama pull llama3.2`

**Vérifier l'installation:**
```bash
ollama list
```

## 📊 Préparation des Données

### Format du fichier d'entrée

Créez `data/input/urls.csv` avec le format suivant :

```csv
code,lien
1,https://example.com/news1
2,https://example.com/news2
...
```

**Colonnes obligatoires:**
- `code` : Identifiant unique (numérique ou alphanumérique)
- `lien` : URL complète de la news

## 🎯 Utilisation

### Option 1 : Exécution complète (recommandée)
bashpython main.py
```

## 📊 Flux d'Exécution
```
main.py
   │
   ├─→ Vérifier fichier d'entrée (urls.csv)
   │
   ├─→ Phase 1: Scraping
   │      │
   │      ├─→ NewsScaper.scrape_all_urls()
   │      └─→ Sauvegarde: scraped_data.csv
   │
   └─→ Phase 2: Analyse LLM
          │
          ├─→ LLMAnalyzer.process_all()
          └─→ Sauvegarde: final_dataset.csv
```

### Option 2 : Exécution par phase

**Phase 1 : Scraping uniquement**
```bash
python main.py --phase scraping
```

**Phase 2 : Analyse LLM uniquement**
```bash
python main.py --phase analysis
```

## 📝 Fichiers de Sortie

### 1. `data/output/scraped_data.csv`
Résultats du scraping (Phase 1) :
- code, url, titre, contenu, langue
- nb_caracteres, nb_mots

### 2. `data/output/final_dataset.csv`
Dataset final complet avec toutes les colonnes :
- Informations de base + analyse LLM
- Date, lieu, maladie, source
- Résumés (50/100/150 mots)
- Animal concerné

## ⚙️ Configuration

### Modifier le LLM utilisé

Éditez `src/config.py` :

```python
LLM_CONFIG = {
    "provider": "ollama",  # ou "openai"
    "model": "llama3.2",   # ou "gpt-3.5-turbo"
    # ...
}
```

### Ajuster les paramètres Selenium

```python
SELENIUM_CONFIG = {
    "headless": True,      # False pour voir le navigateur
    "timeout": 30,         # Timeout en secondes
    # ...
}
```

### Grok / xAI API key (cloud provider)

This project supports using Grok (xAI) in the cloud. The code prefers the variable name `GROQ_API_KEY` (exposed by `src/config.py`) but will fall back to the legacy `GROK_API_KEY` environment variable if present. Set one of these in a `.env` file at the project root or in `src/.env`.

Example `.env` content (never commit real secrets):

```dotenv
# Preferred name used by the code/config
GROQ_API_KEY=sk-<your_real_secret_here>

# Legacy name accepted by the code
GROK_API_KEY=sk-<your_real_secret_here>

# Optional OpenAI key
OPENAI_API_KEY=sk-<your_openai_secret>
```

Notes:
- Make sure you paste the actual secret token (starts with `sk-...`) and do NOT include surrounding quotes.
- If you receive an "Incorrect API key" error from the API, confirm the key is active/valid at https://console.x.ai and was copied fully.

## 🔧 Résolution de Problèmes

### Erreur : "ChromeDriver not found"
```bash
# Le script télécharge automatiquement ChromeDriver
# Si problème persiste :
pip install --upgrade webdriver-manager
```

### Erreur : "Ollama connection refused"
```bash
# Vérifier qu'Ollama est démarré
ollama serve

# Dans un autre terminal
ollama list
```

### Contenu non extrait correctement
- Vérifier que le site n'est pas protégé par Cloudflare/Captcha
- Augmenter le délai dans `scraper.py` (ligne `time.sleep(2)`)
- Désactiver le mode headless pour débugger

### Langue non détectée
- Le texte doit contenir au moins 10 caractères
- Pour l'arabe, vérifier l'encodage UTF-8

## 🎨 Personnalisation

### Ajouter de nouveaux champs

1. Modifier `config.py` :
```python
OUTPUT_COLUMNS = [
    ...,
    "nouveau_champ"
]
```

2. Modifier le prompt dans `llm_analyzer.py`

3. Ajuster `_validate_results()`

### Changer le format de date

Modifier la regex dans `utils.py` :
```python
pattern = r'^\d{2}-\d{2}-\d{4}$'  # jj-mm-aaaa
```

## 📊 Exemples de Résultats

### Exemple de ligne dans le dataset final :

| code | url | titre | langue | maladie | animal | lieu |
|------|-----|-------|--------|---------|--------|------|
| 1 | https://... | Alerte sanitaire | français | fièvre aphteuse | bovins | Normandie |

## 🤝 Alternatives LLM

### Ollama (Recommandé)
✅ Gratuit, local, pas de limite
✅ Multilingue excellent
✅ Pas besoin d'API key

### OpenAI
- Crédit gratuit initial ($5)
- Modifier `LLM_CONFIG` dans config.py
- Ajouter API key dans `.env`

### Groq (Alternative cloud gratuite)
- API gratuite avec limite journalière
- Très rapide
- Modifier config et ajouter `GROQ_API_KEY`

## 📈 Performance

- **Scraping** : ~2-5 secondes par URL
- **Analyse LLM** : ~10-20 secondes par article (Ollama local)
- **50 URLs** : ~15-30 minutes total

## 🐛 Logs

Tous les logs sont dans `data/logs/scraping.log`

```bash
# Voir les logs en temps réel
tail -f data/logs/scraping.log
```

## 📚 Dépendances Principales

- **Selenium** : Automatisation du navigateur
- **BeautifulSoup4** : Parsing HTML
- **pandas** : Manipulation de données
- **langdetect** : Détection de langue
- **ollama** : Interface LLM local

## 💡 Conseils

1. **Testez d'abord sur 5-10 URLs** avant de lancer sur 50
2. **Vérifiez la qualité** du scraping avant l'analyse LLM
3. **Ajustez les timeouts** si les sites sont lents
4. **Utilisez des proxies** si vous scrapez beaucoup d'URLs

## 📞 Support

Pour toute question :
1. Vérifier les logs dans `data/logs/`
2. Tester avec `--phase scraping` d'abord
3. Vérifier qu'Ollama fonctionne : `ollama list`

## 📄 Licence

Projet académique - Utilisez de manière responsable et éthique.

---

**Bon scraping ! 🚀**