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

    # Note: The incident structure might vary slightly between mock and real LLM output.
    # LLM Analyzer output format:
    # { "category", "severity", "summary_en", "source_url", "published_date" }

    # We map this to the requested CSV schema if possible.
    # We might need to generate 'id', 'confidence', 'key_quote' etc if not provided.

    # Ensure columns exist
    for col in ["category", "severity", "summary_en", "source_url", "published_date", "company_name", "ticker"]:
        if col not in df.columns:
            df[col] = None

    # CSV Schema mapping
    df['incident_id'] = df.index + 1 # Simple ID generation
    df['incident_id'] = df.apply(lambda row: f"{row['ticker']}-{row['published_date']}-{row['incident_id']}", axis=1)
    df['confidence'] = "High" # Default from LLM assumption? Or should be in LLM output? LLM output didn't spec it.
    df['key_quote'] = "" # Not in new LLM output spec
    df['source_outlet'] = "Unknown" # Not explicitly in new LLM output spec, but source_url is there.

    final_csv_columns = [
        'incident_id', 'company_name', 'ticker', 'category', 'severity',
        'confidence', 'summary_en', 'key_quote', 'published_date', 'source_url', 'source_outlet'
    ]

    # Filter/Order columns
    for col in final_csv_columns:
        if col not in df.columns:
            df[col] = ""

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
    top_incidents = sorted(all_incidents, key=lambda x: (x.get('severity', 0), x.get('published_date', '')), reverse=True)[:5]
    if not top_incidents:
        top_items_html += "<li>No major incidents this week.</li>"
    else:
        for inc in top_incidents:
            company_name = next((c['company_name'] for c in companies_data if inc in c.get('incidents', [])), "N/A")
            # For new LLM output structure, we just have source_url
            source = f"<a href='{inc.get('source_url', '#')}'>Link</a>"
            top_items_html += f"<li>{company_name} — {inc.get('category', 'N/A')} — Sev {inc.get('severity', 0)}: {inc.get('summary_en', 'No summary.')} [Source: {source}]</li>"
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
            link = f'<a href="{inc.get("source_url", "#")}">Link</a>'
            table_html += f"""
            <tr>
                <td>{company_name}</td>
                <td>{inc.get('category', '')}</td>
                <td>{inc.get('severity', '')}</td>
                <td>{inc.get('published_date', '')}</td>
                <td>{inc.get('summary_en', '')}</td>
                <td>{link}</td>
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

    filepath = os.path.join(OUTPUT_DIR, f"email_body_{week_key}.html")
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
