import os
import requests
import urllib.parse
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        # Map of common languages in your portfolio to ISO 2-letter codes
        # GNews supports: ar, zh, nl, en, fr, de, el, he, hi, it, ja, ml, mr, no, pt, ro, ru, es, sv, ta, te, uk
        mapping = {
            "english": "en",
            "english (us)": "en",
            "english (singapore)": "en",
            "english (israel)": "en",
            "spanish": "es",
            "spanish (uruguay)": "es",
            "french": "fr",
            "german": "de",
            "italian": "it",
            "portuguese": "pt",
            "chinese": "zh",
            "mandarin chinese (traditional)": "zh",
            "japanese": "ja",
            "korean": "ko", # Note: GNews might not fully support KO in free tier, defaulting to broad search if needed
            "hindi": "hi",
            "hebrew": "he",
            "thai": "th", # Note: Check GNews support for TH
            "filipino (tagalog)": "tl", # Note: Check GNews support for TL
            "turkish": "tr", # Note: Check GNews support for TR
            "russian": "ru",
            "dutch": "nl",
            "greek": "el",
            "swedish": "sv",
            "norwegian": "no"
        }

        # Clean input: lowercase and strip whitespace
        clean_name = str(language_name).lower().strip()

        # Return mapped code or default to 'en'
        return mapping.get(clean_name, "en")

    def fetch_company_news(self, company, from_date, to_date):
        """
        Fetch news for a specific company using GNews.io.

        Args:
            company (dict): Company data containing 'company_name', 'aliases', 'local_language'.
            from_date (str): Start date (YYYY-MM-DD).
            to_date (str): End date (YYYY-MM-DD).

        Returns:
            list: A list of standardized article objects.
        """
        articles = []

        # 1. Build Search Queries
        # We construct a boolean query: ("Name" OR "Alias") AND (controversy keywords...)
        # Note: GNews free tier handles simple boolean logic well.

        company_name = company.get('company_name', '')
        aliases = company.get('aliases', [])

        # Create the (Name OR Alias) part
        # Enclose in quotes to ensure exact match for multi-word names
        entity_query_parts = [f'"{company_name}"'] + [f'"{alias}"' for alias in aliases]
        entity_query = "(" + " OR ".join(entity_query_parts) + ")"

        # Keywords for controversy (Broad list to catch issues)
        keywords_en = "(controversy OR scandal OR lawsuit OR fraud OR investigation OR fine OR breach OR violation)"

        # Combine into full query
        full_query_en = f"{entity_query} AND {keywords_en}"

        # 2. Set up request parameters
        # GNews requires dates in ISO 8601 format: YYYY-MM-DDThh:mm:ssZ
        # We assume from_date/to_date come in as YYYY-MM-DD
        from_iso = f"{from_date}T00:00:00Z"
        to_iso = f"{to_date}T23:59:59Z"

        # 3. Request 1: English Search
        params_en = {
            "q": full_query_en,
            "lang": "en",
            "country": "us", # Default to US for English, or remove to search globally
            "max": 10,       # Free tier limit per request
            "from": from_iso,
            "to": to_iso,
            "sortby": "relevance",
            "token": self.api_key
        }

        try:
            # Call API
            logger.info(f"Searching GNews (EN) for {company_name}...")
            response = requests.get(self.base_url, params=params_en)

            if response.status_code == 200:
                data = response.json()
                # Map GNews format to our internal schema
                # GNews format: {'totalArticles': N, 'articles': [{'title':..., 'url':...}]}
                for item in data.get('articles', []):
                    articles.append({
                        "title": item.get('title'),
                        "url": item.get('url'),
                        "published_date": item.get('publishedAt', '')[:10], # Extract YYYY-MM-DD
                        "source": item.get('source', {}).get('name', 'GNews Source'),
                        "snippet": item.get('description', ''),
                        "language": "en"
                    })
            else:
                logger.error(f"GNews API Error (EN): {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"Exception during GNews English search: {e}")

        # 4. Request 2: Local Language Search (if applicable and different from English)
        local_lang_name = company.get('local_language', 'English')
        lang_code = self._get_language_code(local_lang_name)

        if lang_code != 'en':
            # Note: For a production local search, we would ideally translate keywords.
            # For this simplified version, we use the Entity Name + broad English keywords
            # because GNews often indexes international stories with English metadata,
            # OR we rely on the Entity Name finding local articles.

            params_local = {
                "q": entity_query, # Just search the company name in the local language context
                "lang": lang_code,
                "max": 10,
                "from": from_iso,
                "to": to_iso,
                "sortby": "relevance",
                "token": self.api_key
            }

            try:
                logger.info(f"Searching GNews ({lang_code}) for {company_name}...")
                response_loc = requests.get(self.base_url, params=params_local)

                if response_loc.status_code == 200:
                    data_loc = response_loc.json()
                    for item in data_loc.get('articles', []):
                        articles.append({
                            "title": item.get('title'),
                            "url": item.get('url'),
                            "published_date": item.get('publishedAt', '')[:10],
                            "source": item.get('source', {}).get('name', 'GNews Source'),
                            "snippet": item.get('description', ''),
                            "language": lang_code
                        })
                else:
                    logger.warning(f"GNews API Error ({lang_code}): {response_loc.status_code} - {response_loc.text}")

            except Exception as e:
                logger.error(f"Exception during GNews Local search: {e}")

        return articles