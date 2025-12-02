import unittest
import os
import json
from src.output_generator import generate_all_outputs

class TestOutputGenerator(unittest.TestCase):

    def setUp(self):
        self.week_key = "test-2025-W01"
        self.report_data = {
            "week_ending": "2025-01-05",
            "portfolio_summary": {
                "total_incidents": 1,
                "avg_severity": 3.0,
                "count_sev_4_5": 0,
                "trend": "Stable",
                "notes": "Test run"
            },
            "companies": [{
                "company_name": "TestCorp",
                "weekly_metrics": { "trend": "Stable" },
                "ticker": "TC",
                "incidents": [{
                    "id": "TC-2025-01-01-001",
                    "category": "TestCategory",
                    "severity": 3,
                    "summary_en": "A test incident",
                    "confidence": "high",
                    "key_quote": "This is a key quote.",
                    "first_seen": "2025-01-01",
                    "published_date": "2025-01-01",
                    "language": "en",
                    "sources": [{
                        "url": "https://example.com/news",
                        "outlet": "Test News"
                    }]
                }]
            }]
        }
        self.output_dir = "output"
        self.json_path = os.path.join(self.output_dir, f"report-{self.week_key}.json")
        self.csv_path = os.path.join(self.output_dir, f"incidents-{self.week_key}.csv")
        self.html_path = os.path.join(self.output_dir, f"email_body_{self.week_key}.html")

    def tearDown(self):
        for path in [self.json_path, self.csv_path, self.html_path]:
            if os.path.exists(path):
                os.remove(path)

    def test_generate_all_outputs(self):
        generate_all_outputs(self.week_key, self.report_data)

        # Check if all files are created
        self.assertTrue(os.path.exists(self.json_path))
        self.assertTrue(os.path.exists(self.csv_path))
        self.assertTrue(os.path.exists(self.html_path))

        # Verify JSON content
        with open(self.json_path, 'r') as f:
            json_content = json.load(f)
        self.assertEqual(json_content['portfolio_summary']['total_incidents'], 1)

        # Verify CSV content
        import pandas as pd
        df = pd.read_csv(self.csv_path)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['incident_id'], 'TC-2025-01-01-1')


if __name__ == '__main__':
    unittest.main()
