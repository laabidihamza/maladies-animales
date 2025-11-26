import re
from langdetect import detect, LangDetectException
from bs4 import BeautifulSoup

def clean_text(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "lxml")
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text(separator=' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        return "unknown"

def get_domain_type(url: str) -> str:
    # Heuristique simple pour deviner le type de source
    url_lower = url.lower()
    if any(site in url_lower for site in ['facebook.com', 'twitter.com', 'x.com', 'instagram.com', 'linkedin.com']):
        return "réseaux sociaux"
    elif any(site in url_lower for site in ['gov.', 'ministere', 'oie.int', 'fao.org', 'who.int', 'wto.org']):
        return "site officiel"
    else:
        return "médias"