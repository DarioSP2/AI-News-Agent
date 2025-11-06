from datetime import datetime, timedelta

def search_articles(query: str, days: int = 7) -> list[dict]:
    """
    Searches for news articles using a News API.
    This is a mock implementation that returns sample data.
    """
    print(f"Executing MOCK search for: {query}")

    # If the query contains a specific company name, return mock data for it.
    if "Palantir" in query:
        return [
            {
                "url": "https://www.reuters.com/technology/palantir-wins-new-us-army-contract-2025-11-01/",
                "headline": "Palantir wins new US Army contract for battlefield AI",
                "snippet": "Palantir Technologies Inc has been awarded a new contract by the U.S. Army to provide its AI-powered software for battlefield intelligence.",
                "source": "Reuters",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "language": "en"
            },
            {
                "url": "https://www.bloomberg.com/news/articles/2025-11-02/eu-regulators-open-probe-into-palantir-data-practices",
                "headline": "EU Regulators Open Probe into Palantir Data Practices Over Misconduct Allegations",
                "snippet": "The European Union has launched an investigation into Palantir's data handling practices following allegations of misconduct and potential GDPR violations.",
                "source": "Bloomberg",
                "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "language": "en"
            }
        ]

    return []
