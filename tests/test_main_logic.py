import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import pandas as pd
from src.main import calculate_company_metrics, calculate_portfolio_summary, load_portfolio

class TestMainLogic(unittest.TestCase):

    def test_calculate_company_metrics(self):
        incidents = [
            {"category": "Governance/Legal", "severity": 4},
            {"category": "Environmental", "severity": 2}
        ]
        prior_data = {
            "weekly_metrics": {
                "total_incidents": 1,
                "avg_severity": 2.0
            }
        }

        metrics = calculate_company_metrics(incidents, prior_data)

        self.assertEqual(metrics["total_incidents"], 2)
        self.assertEqual(metrics["avg_severity"], 3.0)
        self.assertEqual(metrics["count_sev_4_5"], 1)
        self.assertEqual(metrics["by_category"]["Governance/Legal"], 1)
        self.assertEqual(metrics["wow_delta"]["total_incidents"], 1) # 2 - 1
        self.assertEqual(metrics["wow_delta"]["avg_severity"], 1.0) # 3.0 - 2.0
        self.assertEqual(metrics["trend"], "Worsening")

    def test_calculate_portfolio_summary(self):
        incidents = [
            {"category": "Governance/Legal", "severity": 4},
            {"category": "Environmental", "severity": 2}
        ]
        prior_summary = {
            "total_incidents": 5,
            "avg_severity": 3.0
        }

        summary = calculate_portfolio_summary(incidents, prior_summary)

        self.assertEqual(summary["total_incidents"], 2)
        self.assertEqual(summary["wow_delta"]["total_incidents"], -3)
        self.assertEqual(summary["trend"], "Improving")

    def test_load_portfolio(self):
        csv_content = "name,ticker,aliases\nTest Corp,TC,Alias1,Alias2"
        with patch("pandas.read_csv", return_value=pd.DataFrame([{"name": "Test Corp", "ticker": "TC", "aliases": "Alias1,Alias2"}])):
            data = load_portfolio("dummy.csv")
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["company_name"], "Test Corp")
            self.assertEqual(data[0]["aliases"], ["Alias1", "Alias2"])

if __name__ == '__main__':
    unittest.main()
