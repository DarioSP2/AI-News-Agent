import json

HIGH_PRIORITY_SOURCES = [
    "department of justice", "commission", "court",
    "reuters", "bloomberg", "financial times"
]

def analyze_articles(company_name: str, articles: list[dict]) -> list[dict]:
    """
    Analyzes a list of articles using an LLM to identify and score controversies.
    This is a mock implementation that returns sample data based on headlines.
    """
    print(f"Executing MOCK LLM analysis for {company_name} with {len(articles)} articles.")

    incidents = []

    for i, article in enumerate(articles):
        # Source Weighting
        is_high_priority = any(
            source in article.get("source", "").lower()
            for source in HIGH_PRIORITY_SOURCES
        )

        # In a real implementation, the LLM prompt would be updated to include:
        # "Prioritize facts from primary sources (courts, regulators) over secondary reporting."
        # The `is_high_priority` flag could be used to add this instruction to the prompt.

        # A simple rule-based mock: if a headline contains certain keywords, create an incident.
        if "probe" in article.get("title", "").lower() or "investigation" in article.get("title", "").lower():
            incident = {
                "id": f"{company_name[:3].upper()}-{article.get('published_date', '')}-{i+1}",
                "category": "Governance/Legal",
                "severity": 4 if is_high_priority else 3, # Bump severity for high-priority sources
                "confidence": "high",
                "summary_en": f"Mock summary: An investigation has been opened into {company_name} regarding its data practices, as reported by {article['source']}.",
                "summary_local": "",
                "key_quote": article.get("snippet", ""),
                "sources": [
                    {
                        "url": article.get("url"),
                        "outlet": article.get("source"),
                        "date": article.get("published_date"),
                        "language": article.get("language")
                    }
                ],
                "first_seen": article.get("published_date"),
                "updated": article.get("published_date"),
                "tags": ["investigation", "data privacy"]
            }
            incidents.append(incident)

    return incidents
