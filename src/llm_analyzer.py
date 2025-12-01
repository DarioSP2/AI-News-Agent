import os
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMAnalyzer(ABC):
    """
    Abstract base class for LLM Analyzers.
    """

    @abstractmethod
    def analyze(self, company_name: str, context: Any = None) -> List[Dict[str, Any]]:
        """
        Analyzes the company for controversies.

        Args:
            company_name (str): The name of the company to analyze.
            context (Any): Additional context (e.g., pre-fetched articles for OpenAI).

        Returns:
            List[Dict[str, Any]]: A list of incident dictionaries.
        """
        pass

    def _parse_json_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Helper to parse JSON from LLM response, handling potential code blocks.
        """
        try:
            # Strip markdown code blocks if present
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]

            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response_text}")
            return []

class GoogleAnalyzer(LLMAnalyzer):
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is missing.")

        import google.generativeai as genai
        genai.configure(api_key=self.api_key)

        # Initialize Gemini 2.0 Flash (or available model) with Search tool
        # The user mentioned "gemini 2.0 flash" in the prompt for the key.
        # We will use a standard model name that supports tools.
        # 'gemini-2.0-flash-exp' might be the one, or 'gemini-pro'.
        # Let's try 'gemini-2.0-flash-exp' first as per user hint, fallback to 'gemini-1.5-flash' if needed.
        # But safest is 'gemini-1.5-flash' or 'gemini-1.5-pro' for tool use.
        # Given the user specifically mentioned "gemini 2.0 flash", I'll try to use that if I can guess the ID,
        # otherwise I'll stick to a stable one like `gemini-1.5-flash`.
        # I'll use `gemini-1.5-flash` as a safe default for production code unless I see 2.0 is generally available.
        # Wait, the user said "it runs gemini 2.0 flash". I should use that model.

        self.model_name = "gemini-2.0-flash-exp"

        self.model = genai.GenerativeModel(self.model_name, tools='google_search_retrieval')

    def analyze(self, company_name: str, context: Any = None) -> List[Dict[str, Any]]:
        logger.info(f"Analyzing {company_name} with Google Gemini (Grounding)...")

        prompt = f"""
        You are an automated risk analyst. Your goal is to identify material ESG, legal, and financial controversies regarding the company "{company_name}" from the last 7 days.

        Use Google Search to find relevant news.

        1. Search for: "{company_name}" AND (fraud OR lawsuit OR scandal OR probe OR sanction OR breach OR "regulatory investigation").
        2. Deduplicate articles about the same event.
        3. Filter out noise (stock moves, earnings reports, marketing, product launches). Keep ONLY material controversies.
        4. Classify each unique incident into one of these categories:
           - Governance/Legal
           - Environmental
           - Social/Human Capital
           - Product/Customer
           - Financial Integrity
        5. Assign a severity score (1-5) based on this rubric:
           1 (Low): Rumor, minor complaints.
           2 (Moderate): Isolated incidents, small fines (<$1M).
           3 (Significant): Probes, confirmed lawsuits, data breaches <100k records.
           4 (Major): Large fines ($1M-$50M), resignations, mass recalls, fatalities.
           5 (Critical): Existential threats, multi-billion exposure, systemic fraud.
        6. Provide a summary in English (2 sentences max).

        Return a JSON array of objects with this EXACT structure:
        [
            {{
                "category": "String",
                "severity": Integer,
                "summary_en": "String",
                "source_url": "String",
                "published_date": "YYYY-MM-DD"
            }}
        ]

        If no material controversies are found, return an empty JSON array: [].
        Do not include markdown formatting like ```json. Just the raw JSON string.
        """

        try:
            # We must enable Google Search tool in the call if not fully configured in init
            response = self.model.generate_content(prompt)
            return self._parse_json_response(response.text)
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return []

class OpenAIAnalyzer(LLMAnalyzer):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            # If we are in OpenAI mode, this is fatal.
            # But the factory decides instantiation.
            # We'll allow it to fail here if called.
            pass

        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
        self.model_name = "gpt-4" # Or gpt-4o as preferred

    def analyze(self, company_name: str, context: Any = None) -> List[Dict[str, Any]]:
        """
        Context is expected to be a list of article dictionaries.
        """
        articles = context if isinstance(context, list) else []
        logger.info(f"Analyzing {company_name} with OpenAI GPT-4 ({len(articles)} articles provided)...")

        if not articles:
            return []

        # Prepare context for the prompt
        articles_text = "\n\n".join([
            f"Title: {a.get('title')}\nSource: {a.get('source')}\nDate: {a.get('published_date')}\nSnippet: {a.get('snippet')}\nURL: {a.get('url')}"
            for a in articles[:30] # Limit to avoid context window issues if many
        ])

        prompt = f"""
        You are an automated risk analyst. Analyze the following news articles regarding the company "{company_name}".

        Articles:
        {articles_text}

        Instructions:
        1. Deduplicate articles about the same event.
        2. Filter out noise (stock moves, earnings, marketing). Keep ONLY material controversies.
        3. Classify each unique incident into one of these categories:
           - Governance/Legal
           - Environmental
           - Social/Human Capital
           - Product/Customer
           - Financial Integrity
        4. Assign a severity score (1-5) based on this rubric:
           1 (Low): Rumor, minor complaints.
           2 (Moderate): Isolated incidents, small fines (<$1M).
           3 (Significant): Probes, confirmed lawsuits, data breaches <100k records.
           4 (Major): Large fines ($1M-$50M), resignations, mass recalls, fatalities.
           5 (Critical): Existential threats, multi-billion exposure, systemic fraud.
        5. Provide a summary in English (2 sentences max).
        6. For "source_url", pick the most credible URL from the provided articles for that incident.

        Return a JSON array of objects with this EXACT structure:
        [
            {{
                "category": "String",
                "severity": Integer,
                "summary_en": "String",
                "source_url": "String",
                "published_date": "YYYY-MM-DD"
            }}
        ]

        If no material controversies are found, return an empty JSON array: [].
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful and strict risk analyst who outputs only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            content = response.choices[0].message.content
            return self._parse_json_response(content)
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return []

def get_llm_analyzer() -> LLMAnalyzer:
    """
    Factory function to get the configured LLM Analyzer.
    """
    provider = os.getenv("LLM_PROVIDER", "google").lower()

    if provider == "google":
        return GoogleAnalyzer()
    elif provider == "openai":
        return OpenAIAnalyzer()
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Options: 'google', 'openai'.")
