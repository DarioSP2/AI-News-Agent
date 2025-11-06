import unittest
import os
import json
from src.state_manager import save_state, load_prior_state

class TestStateManager(unittest.TestCase):

    def setUp(self):
        self.week_key = "test-2025-W01"
        self.report_data = {"portfolio_summary": {"total_incidents": 5}}
        self.filepath = os.path.join("reports", f"report-{self.week_key}.json")

    def tearDown(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    def test_save_and_load_state(self):
        # Test saving the state
        save_state(self.week_key, self.report_data)
        self.assertTrue(os.path.exists(self.filepath))

        # Test loading the state
        loaded_data = load_prior_state(self.week_key)
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data, self.report_data)

    def test_load_non_existent_state(self):
        # Test loading a state that doesn't exist
        loaded_data = load_prior_state("non-existent-key")
        self.assertIsNone(loaded_data)

if __name__ == '__main__':
    unittest.main()
