import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.state_manager import load_prior_state, save_state
from src.output_generator import generate_all_outputs
from src.news_api import NewsAPI
from src.llm_analyzer import analyze_articles

# Load environment variables from .env file
load_dotenv()

def load_portfolio(filepath: str) -> list[dict]:
    """Loads the portfolio data from a CSV file."""
    df = pd.read_csv(filepath)
    df.rename(columns={"name": "company_name"}, inplace=True)
    df['aliases'] = df['aliases'].apply(lambda x: x.split(',') if isinstance(x, str) else [])
    return df.to_dict("records")

def calculate_company_metrics(incidents: list, prior_company_data: dict | None) -> dict:
    """Calculates metrics for a single company."""
    total_incidents = len(incidents)
    avg_severity = sum(i['severity'] for i in incidents) / total_incidents if total_incidents > 0 else 0.0
    count_sev_4_5 = sum(1 for i in incidents if i['severity'] >= 4)

    by_category = {}
    for incident in incidents:
        cat = incident['category']
        by_category[cat] = by_category.get(cat, 0) + 1

    wow_delta = {}
    if prior_company_data:
        wow_delta["total_incidents"] = total_incidents - prior_company_data["weekly_metrics"]["total_incidents"]
        wow_delta["avg_severity"] = avg_severity - prior_company_data["weekly_metrics"]["avg_severity"]

    trend = "Stable"
    if wow_delta.get("total_incidents", 0) > 0:
        trend = "Worsening"
    elif wow_delta.get("total_incidents", 0) < 0:
        trend = "Improving"

    return {
        "total_incidents": total_incidents,
        "avg_severity": avg_severity,
        "count_sev_4_5": count_sev_4_5,
        "by_category": by_category,
        "wow_delta": wow_delta,
        "trend": trend
    }

def calculate_portfolio_summary(all_incidents: list, prior_summary: dict | None) -> dict:
    """Aggregates metrics for the entire portfolio."""
    total_incidents = len(all_incidents)
    avg_severity = sum(i['severity'] for i in all_incidents) / total_incidents if total_incidents > 0 else 0.0
    count_sev_4_5 = sum(1 for i in all_incidents if i['severity'] >= 4)

    by_category = {}
    for incident in all_incidents:
        cat = incident['category']
        by_category[cat] = by_category.get(cat, 0) + 1

    wow_delta = {}
    if prior_summary:
        wow_delta["total_incidents"] = total_incidents - prior_summary["total_incidents"]
        wow_delta["avg_severity"] = avg_severity - prior_summary["avg_severity"]

    trend = "Stable"
    if wow_delta.get("total_incidents", 0) > 0:
        trend = "Worsening"
    elif wow_delta.get("total_incidents", 0) < 0:
        trend = "Improving"

    return {
        "total_incidents": len(all_incidents),
        "avg_severity": avg_severity,
        "count_sev_4_5": count_sev_4_5,
        "by_category": by_category,
        "wow_delta": wow_delta,
        "trend": trend,
        "notes": "Initial run, no trend data available." if not prior_summary else "Week-over-week comparison."
    }

def deliver_and_save_state(week_key: str, report: dict):
    """Placeholder: Sends email and saves the current week's report."""
    print(f"Delivering email report for {week_key}.")
    save_state(week_key, report)
    # In a real implementation, this would use an email API
    pass

def main():
    """Main orchestration function."""
    # 1. Initialize
    run_date = datetime.now()
    week_key = f"PortfolioName-{run_date.year}-W{run_date.isocalendar()[1]}"
    from_date = (run_date - timedelta(days=7)).strftime("%Y-%m-%d")
    to_date = run_date.strftime("%Y-%m-%d")
    last_week_key = f"PortfolioName-{(run_date - timedelta(days=7)).year}-W{(run_date - timedelta(days=7)).isocalendar()[1]}"

    print(f"Starting weekly controversy monitoring run for: {week_key}")

    # Initialize News API client
    news_api = NewsAPI()

    portfolio_data = load_portfolio("data/enriched_portfolio.csv")

    # 2. Load Prior State
    prior_state = load_prior_state(last_week_key)
    prior_summary = prior_state.get("portfolio_summary") if prior_state else None
    prior_companies = {c["company_name"]: c for c in prior_state.get("companies", [])} if prior_state else {}

    # 3. Loop Companies
    all_incidents = []
    output_companies_data = []
    for company in portfolio_data:
        company_name = company["company_name"]
        print(f"--- Processing: {company_name} ---")

        # B. Execute Search
        raw_articles = news_api.fetch_company_news(company, from_date, to_date)

        if not raw_articles:
            print(f"No articles found for {company_name}. Skipping.")
            company_metrics = calculate_company_metrics([], prior_companies.get(company_name))
            company_report = {"company_name": company_name, "ticker": company["ticker"], "incidents": [], "weekly_metrics": company_metrics}
            output_companies_data.append(company_report)
            continue

        # C. Analyze & Score (LLM Call)
        company_incidents = analyze_articles(company_name, raw_articles)
        all_incidents.extend(company_incidents)

        # E. Calculate Company Metrics
        company_metrics = calculate_company_metrics(company_incidents, prior_companies.get(company_name))

        company_report = {
            "company_name": company_name,
            "ticker": company["ticker"],
            "incidents": company_incidents,
            "weekly_metrics": company_metrics
        }
        output_companies_data.append(company_report)

    # 4. Calculate Portfolio Summary
    portfolio_summary = calculate_portfolio_summary(all_incidents, prior_summary)

    # 5. Generate Outputs
    final_report = {
        "week_ending": to_date,
        "portfolio_summary": portfolio_summary,
        "companies": output_companies_data
    }
    generate_all_outputs(week_key, final_report)

    # 6. Deliver & Save State
    deliver_and_save_state(week_key, final_report)

    print("--- Run Complete ---")


if __name__ == "__main__":
    main()
