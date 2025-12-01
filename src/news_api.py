import os
import json
from google import genai
from google.genai import types
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsAPI:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not found.")
            raise ValueError("Please add GOOGLE_API_KEY to your .env file.")

        self.client = genai.Client(api_key=self.api_key)

    def fetch_company_news(self, company, from_date, to_date):
        """
        Uses Gemini with Google Search Grounding to find news and format it as JSON.
        """
        articles = []
        company_name = company.get('company_name', '')

        prompt = f"""
        You are a news aggregator. Perform a Google Search for recent news about "{company_name}"
        between {from_date} and {to_date}.

        Focus specifically on these topics: controversy, scandal, investigation, lawsuit, fine, recall, sanction.

        Return a strict JSON list of the top 5 most relevant articles found.
        The JSON must follow this format exactly:
        [
            {{
                "title": "Article Headline",
                "url": "https://link.to.article",
                "published_date": "YYYY-MM-DD",
                "source": "Publisher Name",
                "snippet": "Brief summary of the article content."
            }}
        ]

        If no relevant controversy news is found, return an empty JSON list: []
        Do not include markdown formatting (like ```json), just the raw JSON string.
        """

        try:
            logger.info(f"Asking Gemini to search news for {company_name}...")

            response = self.client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                tools=[types.Tool(google_search=types.GoogleSearch())],
                generation_config=types.GenerationConfig(
                    temperature=0.0
                ),
                safety_settings={
                    types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: types.HarmBlockThreshold.BLOCK_NONE,
                    types.HarmCategory.HARM_CATEGORY_HARASSMENT: types.HarmBlockThreshold.BLOCK_NONE,
                    types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: types.HarmBlockThreshold.BLOCK_NONE,
                    types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: types.HarmBlockThreshold.BLOCK_NONE,
                }
            )

            text_response = response.text.strip()

            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]

            data = json.loads(text_response)

            if isinstance(data, list):
                for item in data:
                    articles.append({
                        "title": item.get('title', 'No Title'),
                        "url": item.get('url', '#'),
                        "published_date": item.get('published_date', from_date),
                        "source": item.get('source', 'Google Search'),
                        "snippet": item.get('snippet', ''),
                        "language": "en"
                    })
            else:
                logger.warning(f"Gemini returned invalid JSON structure: {text_response[:100]}...")

        except Exception as e:
            logger.error(f"Exception during Gemini Search: {e}")

        return articles
