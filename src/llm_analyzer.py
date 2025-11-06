import json

def analyze_articles(company_name: str, articles: list[dict]) -> list[dict]:
    """
    Analyzes a list of articles using an LLM to identify and score controversies.
    This is a mock implementation that returns sample data based on headlines.
    """
    print(f"Executing MOCK LLM analysis for {company_name} with {len(articles)} articles.")

    incidents = []

    for i, article in enumerate(articles):
        # A simple rule-based mock: if a headline contains certain keywords, create an incident.
        if "probe" in article.get("headline", "").lower() or "investigation" in article.get("headline", "").lower():
            incident = {
                "id": f"{company_name[:3].upper()}-{article['date']}-{i+1}",
                "category": "Governance/Legal",
                "severity": 3,
                "confidence": "high",
                "summary_en": f"Mock summary: An investigation has been opened into {company_name} regarding its data practices, as reported by {article['source']}.",
                "summary_local": "",
                "key_quote": article.get("snippet", ""),
                "sources": [
                    {
                        "url": article.get("url"),
                        "outlet": article.get("source"),
                        "date": article.get("date"),
                        "language": article.get("language")
                    }
                ],
                "first_seen": article.get("date"),
                "updated": article.get("date"),
                "tags": ["investigation", "data privacy"]
            }
            incidents.append(incident)

    return incidents
