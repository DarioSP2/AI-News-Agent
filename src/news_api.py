import os
import requests
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONTROVERSY_KEYWORDS = {
    # English: No multi-word phrases, simple parenthesis
    "en": "(controversy OR scandal OR probe OR investigation OR lawsuit OR fine OR recall OR breach OR sanction OR misconduct)",

    # Spanish: Use \" for "mala conducta"
    "es": "(polémica OR escándalo OR investigación OR demanda OR multa OR retirada OR sanción OR \"mala conducta\" OR infracción)",

    # Portuguese: Use \" for "má conduta"
    "pt": "(polêmica OR escândalo OR investigação OR processo OR multa OR recall OR violação OR sanção OR \"má conduta\")",

    # French: Use \" for "mauvaise conduite"
    "fr": "(controverse OR scandale OR enquête OR procès OR amende OR rappel OR infraction OR sanction OR \"mauvaise conduite\")",

    # German: No multi-word phrases usually needed for these terms
    "de": "(Kontroverse OR Skandal OR Ermittlung OR Klage OR Geldstrafe OR Rückruf OR Verstoß OR Sanktion OR Fehlverhalten)",

    # Italian: Simple terms
    "it": "(controversia OR scandalo OR indagine OR causa OR multa OR richiamo OR violazione OR sanzione)",
}

class NewsAPI:
    def __init__(self):
        """
        Initialize the GNews client.
        """
        self.api_key = os.getenv("NEWS_API_KEY")
        if not self.api_key:
            logger.error("NEWS_API_KEY not found in environment variables.")
            raise ValueError("NEWS_API_KEY is missing. Please add it to your .env file.")

        self.base_url = "https://gnews.io/api/v4/search"

    def _get_language_code(self, language_name):
        """
        Helper to map full language names (from CSV) to GNews 2-letter codes.
        Defaults to 'en' (English) if not found.
        """
        mapping = {
            "english": "en", "english (us)": "en", "english (singapore)": "en", "english (israel)": "en",
            "spanish": "es", "spanish (uruguay)": "es",
            "french": "fr", "german": "de", "italian": "it", "portuguese": "pt",
            "chinese": "zh", "mandarin chinese (traditional)": "zh",
            "japanese": "ja", "korean": "ko", "hindi": "hi", "hebrew": "he", "thai": "th",
            "filipino (tagalog)": "tl", "turkish": "tr", "russian": "ru",
            "dutch": "nl", "greek": "el", "swedish": "sv", "norwegian": "no"
        }
        return mapping.get(str(language_name).lower().strip(), "en")

    def fetch_company_news(self, company, from_date, to_date):
        """
        Fetch news for a specific company using GNews.io.
        Order: Local Language (if applicable) -> English.
        """
        articles = []
        company_name = company.get('company_name', '')

        # Determine Local Language
        local_lang_name = company.get('local_language', 'English')
        lang_code = self._get_language_code(local_lang_name)

        # --- Request 1: Local Language Search (Priority) ---
        if lang_code != 'en':
            local_keywords = CONTROVERSY_KEYWORDS.get(lang_code, CONTROVERSY_KEYWORDS['en'])
            query_local = f'"{company_name}" AND {local_keywords}'
            # We don't restrict country for local search to be broader, or we could if mapped.
            articles.extend(self._execute_gnews_search(query_local, lang_code, None, from_date, to_date, company_name))

        # --- Request 2: English Search ---
        query_en = f'"{company_name}" AND {CONTROVERSY_KEYWORDS["en"]}'
        # Prioritize US news for English, but maybe we should relax country if company is global?
        # Current code uses "us". Keeping it for now.
        articles.extend(self._execute_gnews_search(query_en, "en", "us", from_date, to_date, company_name))

        return articles

    def _execute_gnews_search(self, query, lang_code, country_code, from_date, to_date, company_name):
        """Helper to execute a single search request to GNews."""
        fetched_articles = []
        params = {
            "q": query,
            "lang": lang_code,
            "max": 10,
            "from": f"{from_date}T00:00:00Z",
            "to": f"{to_date}T23:59:59Z",
            "sortby": "relevance",
            "token": self.api_key
        }
        if country_code:
            params["country"] = country_code

        try:
            logger.info(f"Searching GNews ({lang_code.upper()}) for {company_name}...")
            response = requests.get(self.base_url, params=params)

            if response.status_code == 200:
                data = response.json()
                for item in data.get('articles', []):
                    fetched_articles.append({
                        "title": item.get('title'),
                        "url": item.get('url'),
                        "published_date": item.get('publishedAt', '')[:10],
                        "source": item.get('source', {}).get('name', 'GNews Source'),
                        "snippet": item.get('description', ''),
                        "language": lang_code
                    })
            else:
                logger.error(f"GNews API Error ({lang_code.upper()}): {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"Exception during GNews {lang_code.upper()} search: {e}")

        return fetched_articles
