import json
import os
import pandas as pd

OUTPUT_DIR = "output"

def generate_report_json(week_key: str, report: dict):
    """Generates the report.json file."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    filepath = os.path.join(OUTPUT_DIR, f"report-{week_key}.json")
    with open(filepath, "w") as f:
        json.dump(report, f, indent=2)
    print(f"report.json saved to {filepath}")

def generate_incidents_csv(week_key: str, all_incidents: list):
    """Generates the incidents.csv file."""
    if not all_incidents:
        print("No incidents to generate CSV for.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    df = pd.json_normalize(all_incidents)
    # Select and rename columns as per schema
    # This is a simplified version, more complex logic might be needed for nested sources
    df = df.rename(columns={
        "id": "incident_id",
        "summary_en": "summary_en",
        "first_seen": "first_seen_date"
    })
    # Add company info if not present
    # df['company_name'] = ...

    filepath = os.path.join(OUTPUT_DIR, f"incidents-{week_key}.csv")
    df.to_csv(filepath, index=False)
    print(f"incidents.csv saved to {filepath}")


def generate_email_body(week_key: str, summary: dict, companies_data: list, all_incidents: list) -> str:
    """Generates the HTML email body."""
    # This is a simplified template population
    html = f"""
    <h1>Weekly Controversy Scan: {week_key}</h1>
    <h2>Portfolio Snapshot</h2>
    <ul>
        <li>Total incidents: {summary.get('total_incidents', 0)}</li>
        <li>Avg severity: {summary.get('avg_severity', 0.0)}</li>
        <li>Major (4–5): {summary.get('count_sev_4_5', 0)}</li>
        <li>Trend: <b>{summary.get('trend', 'N/A')}</b> — {summary.get('notes', '')}</li>
    </ul>
    """

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    filepath = os.path.join(OUTPUT_DIR, f"email_body-{week_key}.html")
    with open(filepath, "w") as f:
        f.write(html)
    print(f"email_body.html saved to {filepath}")
    return html

def generate_all_outputs(week_key: str, report: dict):
    """Generates all output files."""
    summary = report.get("portfolio_summary", {})
    companies_data = report.get("companies", [])
    all_incidents = []
    for company in companies_data:
        all_incidents.extend(company.get("incidents", []))

    generate_report_json(week_key, report)
    generate_incidents_csv(week_key, all_incidents)
    generate_email_body(week_key, summary, companies_data, all_incidents)
