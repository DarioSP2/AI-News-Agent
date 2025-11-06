import os
import pandas as pd
from datetime import datetime, timedelta
from src.state_manager import load_prior_state, save_state
from src.output_generator import generate_all_outputs
from src.news_api import search_articles
from src.llm_analyzer import analyze_articles

def load_portfolio(filepath: str) -> list[dict]:
    """Loads the portfolio data from a CSV file."""
    df = pd.read_csv(filepath)
    df.rename(columns={"name": "company_name"}, inplace=True)
    # Ensure aliases are lists
    df['aliases'] = df['aliases'].apply(lambda x: x.split(',') if isinstance(x, str) else [])
    return df.to_dict("records")

def build_search_queries(company: dict) -> tuple[str, str]:
    """Builds English and local language search queries."""
    # This is a simplified version of the query logic
    base_terms = [f'"{company["company_name"]}"'] + [f'"{alias}"' for alias in company.get('aliases', [])]
    company_query = " OR ".join(base_terms)
    controversy_terms_en = "controversy OR scandal OR probe OR investigation OR lawsuit OR fine"

    english_query = f"({company_query}) AND ({controversy_terms_en})"
    # Local language query would involve translation
    local_language_query = english_query

    print(f"Generated EN query for {company['company_name']}: {english_query}")
    return english_query, local_language_query

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
    last_week = run_date - timedelta(days=7)
    last_week_key = f"PortfolioName-{last_week.year}-W{last_week.isocalendar()[1]}"

    print(f"Starting weekly controversy monitoring run for: {week_key}")

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

        # A. Build Queries
        en_query, local_query = build_search_queries(company)

        # B. Execute Search
        articles_en = search_articles(en_query, days=7)
        articles_local = search_articles(local_query, days=7)
        raw_articles = articles_en + articles_local

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
        "week_ending": run_date.strftime("%Y-%m-%d"),
        "portfolio_summary": portfolio_summary,
        "companies": output_companies_data
    }
    generate_all_outputs(week_key, final_report)

    # 6. Deliver & Save State
    deliver_and_save_state(week_key, final_report)

    print("--- Run Complete ---")


if __name__ == "__main__":
    main()
