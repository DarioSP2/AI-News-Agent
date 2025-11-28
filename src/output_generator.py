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

def generate_incidents_csv(week_key: str, companies_data: list):
    """Generates the incidents.csv file."""
    all_incidents_with_company_info = []
    for company in companies_data:
        for incident in company.get("incidents", []):
            incident_copy = incident.copy()
            incident_copy["company_name"] = company.get("company_name")
            incident_copy["ticker"] = company.get("ticker")
            all_incidents_with_company_info.append(incident_copy)

    if not all_incidents_with_company_info:
        print("No incidents to generate CSV for.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    df = pd.json_normalize(all_incidents_with_company_info)

    # Define the columns required by the schema
    schema_columns = [
        "id", "company_name", "ticker", "category", "severity",
        "confidence", "summary_en", "key_quote", "first_seen",
        "language", "sources"
    ]

    # Select and rename columns as per schema
    # Create a mapping for renaming
    rename_mapping = {
        "id": "incident_id",
        "first_seen": "first_seen_date"
    }

    # Extract source info
    df['source_url'] = df['sources'].apply(lambda x: x[0]['url'] if x and isinstance(x, list) else None)
    df['source_outlet'] = df['sources'].apply(lambda x: x[0]['outlet'] if x and isinstance(x, list) else None)


    # Filter for columns that exist in the dataframe to avoid KeyErrors
    existing_cols_to_rename = {k: v for k, v in rename_mapping.items() if k in df.columns}
    df = df.rename(columns=existing_cols_to_rename)

    # The final list of columns for the CSV
    final_csv_columns = ['incident_id', 'company_name', 'ticker', 'category', 'severity', 'confidence', 'summary_en', 'key_quote', 'first_seen_date', 'source_url', 'source_outlet']

    filepath = os.path.join(OUTPUT_DIR, f"incidents-{week_key}.csv")
    df.to_csv(filepath, index=False, columns=final_csv_columns)
    print(f"incidents.csv saved to {filepath}")


def generate_email_body(week_key: str, summary: dict, companies_data: list, all_incidents: list) -> str:
    """Generates the HTML email body."""

    # --- Helper functions for formatting ---
    def format_delta(value, key):
        if not summary.get("wow_delta"): return ""
        delta = summary["wow_delta"].get(key, 0)
        sign = "+" if delta > 0 else ""
        color = "red" if delta > 0 else "green" if delta < 0 else "gray"
        return f' (Δ WoW: <span style="color:{color};">{sign}{delta}</span>)'

    # --- Portfolio Snapshot ---
    snapshot_html = f"""
    <h3>Portfolio Snapshot</h3>
    <ul>
        <li>Total incidents: {summary.get('total_incidents', 0)}{format_delta(summary.get('total_incidents'), 'total_incidents')}</li>
        <li>Avg severity: {summary.get('avg_severity', 0.0):.2f}{format_delta(summary.get('avg_severity'), 'avg_severity')}</li>
        <li>Major (4–5): {summary.get('count_sev_4_5', 0)}</li>
        <li>Trend: <b>{summary.get('trend', 'N/A')}</b> — {summary.get('notes', '')}</li>
    </ul>
    """

    # --- Top Items ---
    top_items_html = "<h3>Top Items (by severity & recency)</h3><ol>"
    # Sort incidents by severity (desc) and date (desc)
    top_incidents = sorted(all_incidents, key=lambda x: (x.get('severity', 0), x.get('first_seen', '')), reverse=True)[:5]
    if not top_incidents:
        top_items_html += "<li>No major incidents this week.</li>"
    else:
        for inc in top_incidents:
            company_name = next((c['company_name'] for c in companies_data if inc in c.get('incidents', [])), "N/A")
            outlets = ", ".join([s.get('outlet', 'N/A') for s in inc.get('sources', [])])
            top_items_html += f"<li>{company_name} — {inc.get('category', 'N/A')} — Sev {inc.get('severity', 0)}: {inc.get('summary_en', 'No summary.')} [Sources: {outlets}]</li>"
    top_items_html += "</ol>"

    # --- Company Trends ---
    trends_html = "<h3>Company-level Trend Highlights</h3><ul>"
    improving = [c['company_name'] for c in companies_data if c['weekly_metrics']['trend'] == 'Improving']
    worsening = [c['company_name'] for c in companies_data if c['weekly_metrics']['trend'] == 'Worsening']
    trends_html += f"<li><b>Improving:</b> {', '.join(improving) if improving else 'None'}</li>"
    trends_html += f"<li><b>Worsening:</b> {', '.join(worsening) if worsening else 'None'}</li>"
    trends_html += "</ul>"

    # --- Full Incident Table ---
    table_html = """
    <h3>Full Incident Table (past 7 days)</h3>
    <table border="1" cellpadding="5" cellspacing="0">
        <thead>
            <tr>
                <th>Company</th><th>Category</th><th>Sev</th><th>Date</th><th>Summary</th><th>Sources</th>
            </tr>
        </thead>
        <tbody>
    """
    if not all_incidents:
        table_html += '<tr><td colspan="6">No incidents found.</td></tr>'
    else:
        for inc in all_incidents:
            company_name = next((c['company_name'] for c in companies_data if inc in c.get('incidents', [])), "N/A")
            links = ", ".join([f'<a href="{s.get("url", "#")}">{s.get("outlet", "Link")}</a>' for s in inc.get("sources", [])])
            table_html += f"""
            <tr>
                <td>{company_name}</td>
                <td>{inc.get('category', '')}</td>
                <td>{inc.get('severity', '')}</td>
                <td>{inc.get('first_seen', '')}</td>
                <td>{inc.get('summary_en', '')}</td>
                <td>{links}</td>
            </tr>
            """
    table_html += "</tbody></table>"

    # --- Assemble Final HTML ---
    full_html = f"""
    <p>Hi Dario,</p>
    <p>Here’s the weekly controversy scan for your portfolio (week ending {week_key}).</p>
    {snapshot_html}
    {top_items_html}
    {trends_html}
    {table_html}
    <br>
    <p>Attachments: Full JSON + CSV</p>
    <p>— Your automated agent</p>
    """

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    filepath = os.path.join(OUTPUT_DIR, f"email_body-{week_key}.html")
    with open(filepath, "w") as f:
        f.write(full_html)
    print(f"email_body.html saved to {filepath}")
    return full_html

def generate_all_outputs(week_key: str, report: dict):
    """Generates all output files."""
    summary = report.get("portfolio_summary", {})
    companies_data = report.get("companies", [])

    all_incidents = []
    for company in companies_data:
        all_incidents.extend(company.get("incidents", []))

    generate_report_json(week_key, report)
    generate_incidents_csv(week_key, companies_data)
    generate_email_body(week_key, summary, companies_data, all_incidents)
