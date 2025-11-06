import json
import os

REPORTS_DIR = "reports"

def save_state(week_key: str, report: dict):
    """Saves the weekly report to a JSON file."""
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    filepath = os.path.join(REPORTS_DIR, f"report-{week_key}.json")
    with open(filepath, "w") as f:
        json.dump(report, f, indent=2)
    print(f"State saved to {filepath}")

def load_prior_state(week_key: str) -> dict | None:
    """Loads a previous week's report from a JSON file."""
    filepath = os.path.join(REPORTS_DIR, f"report-{week_key}.json")
    if not os.path.exists(filepath):
        print(f"No prior state found for week: {week_key}")
        return None

    with open(filepath, "r") as f:
        print(f"Prior state loaded from {filepath}")
        return json.load(f)
