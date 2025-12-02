import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import json
from src.llm_analyzer import get_llm_analyzer, GoogleAnalyzer, OpenAIAnalyzer, LLMAnalyzer

class TestLLMAnalyzer(unittest.TestCase):

    def setUp(self):
        self.original_env = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_factory_google(self):
        os.environ["LLM_PROVIDER"] = "google"
        os.environ["GOOGLE_API_KEY"] = "fake_key"

        # Mocking genai to avoid actual init
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel"):
            analyzer = get_llm_analyzer()
            self.assertIsInstance(analyzer, GoogleAnalyzer)

    def test_factory_openai(self):
        os.environ["LLM_PROVIDER"] = "openai"
        os.environ["OPENAI_API_KEY"] = "fake_key"

        with patch("openai.OpenAI"):
            analyzer = get_llm_analyzer()
            self.assertIsInstance(analyzer, OpenAIAnalyzer)

    def test_google_analyzer_prompt_structure(self):
        os.environ["GOOGLE_API_KEY"] = "fake_key"

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '[]'
        mock_model.generate_content.return_value = mock_response

        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel", return_value=mock_model):
            analyzer = GoogleAnalyzer()
            analyzer.analyze("Test Corp")

            # Verify generate_content was called
            self.assertTrue(mock_model.generate_content.called)
            # Verify tools config was passed in init (implicitly checked by patching GenerativeModel)

            # Verify prompt contains key instructions
            args, _ = mock_model.generate_content.call_args
            prompt = args[0]
            self.assertIn("Test Corp", prompt)
            self.assertIn("Google Search", prompt)
            self.assertIn("JSON array", prompt)

    def test_openai_analyzer_prompt_structure(self):
        os.environ["OPENAI_API_KEY"] = "fake_key"

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='[]'))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch("openai.OpenAI", return_value=mock_client):
            analyzer = OpenAIAnalyzer()
            articles = [{"title": "Bad News", "source": "News", "published_date": "2023-01-01", "snippet": "Bad things", "url": "http://example.com"}]
            analyzer.analyze("Test Corp", context=articles)

            # Verify create was called
            self.assertTrue(mock_client.chat.completions.create.called)

            # Verify prompt content
            kwargs = mock_client.chat.completions.create.call_args.kwargs
            messages = kwargs['messages']
            user_content = messages[1]['content']
            self.assertIn("Test Corp", user_content)
            self.assertIn("Bad News", user_content)

    def test_json_parsing(self):
        # Test helper method on a concrete subclass instance
        os.environ["GOOGLE_API_KEY"] = "fake_key"
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel"):
            analyzer = GoogleAnalyzer()

            # Case 1: Pure JSON
            res = analyzer._parse_json_response('[{"test": 1}]')
            self.assertEqual(res, [{"test": 1}])

            # Case 2: Markdown block
            res = analyzer._parse_json_response('```json\n[{"test": 2}]\n```')
            self.assertEqual(res, [{"test": 2}])

            # Case 3: Invalid JSON
            res = analyzer._parse_json_response('Not JSON')
            self.assertEqual(res, [])

if __name__ == '__main__':
    unittest.main()
