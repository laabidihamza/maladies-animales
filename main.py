import pandas as pd
from src.scraper import setup_driver, extract_article_data
from src.utils import clean_text, detect_language, get_domain_type
from src.llm_processor import extract_fields_with_llm
import logging
import time

INPUT_FILE = "data/input_urls.csv"
OUTPUT_FILE = "data/output_dataset.csv"

def main():
    df_input = pd.read_csv(INPUT_FILE)
    driver = setup_driver()

    results = []

    for idx, row in df_input.iterrows():
        code = row['code']
        url = row['lien']

        logging.info(f"Traitement [{code}] : {url}")

        # Phase 1 : Scraping
        raw_data = extract_article_data(driver, url)
        contenu_clean = clean_text(raw_data["contenu"])
        langue = detect_language(contenu_clean)
        source_type = get_domain_type(url)

        # Phase 2 : LLM
        llm_fields = extract_fields_with_llm(contenu_clean, url)

        # Compter caractères et mots
        nb_caracteres = len(contenu_clean)
        nb_mots = len(contenu_clean.split())

        # Construire la ligne finale
        final_row = {
            "code": code,
            "url": url,
            "titre": raw_data["titre"],
            "contenu": contenu_clean,
            "langue": langue,
            "nb_caracteres": nb_caracteres,
            "nb_mots": nb_mots,
            "date_publication": llm_fields["date_publication"],
            "lieu": llm_fields["lieu"],
            "maladie": llm_fields["maladie"],
            "animal": llm_fields["animal"],
            "source_publication": source_type,
            "resume_50_mots": llm_fields["resume_50_mots"],
            "resume_100_mots": llm_fields["resume_100_mots"],
            "resume_150_mots": llm_fields["resume_150_mots"]
        }

        results.append(final_row)

        # Sauvegarde partielle (au cas où)
        pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)

        time.sleep(1)  # Être gentil avec les serveurs

    driver.quit()
    logging.info("✅ Scraping et traitement terminés.")

if __name__ == "__main__":
    main()