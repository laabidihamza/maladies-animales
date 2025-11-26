import ollama
import re

MODEL = "llama3.2"  # ou "mistral", "gemma2:9b" selon vos tests

def query_ollama(prompt: str) -> str:
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1}  # pour plus de déterminisme
        )
        return response["message"]["content"].strip()
    except Exception as e:
        return f"[Erreur LLM: {str(e)}]"

def extract_fields_with_llm(text: str, url: str):
    # Prompt général pour extraire tous les champs
    prompt = f"""
Tu es un assistant expert en santé animale. Analyse le texte suivant et extrais les informations demandées. Réponds strictement en format JSON avec les clés suivantes : 
- "date_publication" (format jj-mm-aaaa, "inconnue" si absente)
- "lieu" (pays ou région mentionnée, "inconnu" si absente)
- "maladie" (nom de la maladie animale, "inconnue" si absente)
- "animal" (espèce animale concernée, "inconnu" si absente)
- "resume_50_mots"
- "resume_100_mots"
- "resume_150_mots"

Règles :
- Les résumés doivent être en français, informatifs, et avoir EXACTEMENT le nombre de mots demandé.
- Ne jamais inventer d'informations.
- Si une info n'est pas dans le texte, mets "inconnu(e)".

Texte à analyser :
{text[:4000]}  # Limite raisonnable pour le contexte
"""

    raw_response = query_ollama(prompt)

    # Extraire le JSON même si entouré de texte
    json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
    if json_match:
        import json
        try:
            return json.loads(json_match.group())
        except:
            pass

    # Échec → valeurs par défaut
    return {
        "date_publication": "inconnue",
        "lieu": "inconnu",
        "maladie": "inconnue",
        "animal": "inconnu",
        "resume_50_mots": "Résumé indisponible.",
        "resume_100_mots": "Résumé indisponible.",
        "resume_150_mots": "Résumé indisponible."
    }