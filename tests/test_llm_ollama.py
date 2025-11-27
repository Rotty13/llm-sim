"""
Unit tests for the LLM class in llm_ollama.py.
"""
import unittest
from unittest.mock import patch, MagicMock
from sim.llm.llm_ollama import LLM

class TestLLM(unittest.TestCase):

    def setUp(self):
        self.llm = LLM()

    @patch("sim.llm.llm_ollama.requests.post")
    def test_chat(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"message": {"content": "Hello!"}}

        response = self.llm.chat("Hi")
        self.assertEqual(response, "Hello!")

    @patch("sim.llm.llm_ollama.requests.post")
    def test_chat_json(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"message": {"content": "{"key": "value"}"}}

        response = self.llm.chat_json("Hi")
        self.assertEqual(response, {"key": "value"})

    @patch("sim.llm.llm_ollama.requests.post")
    def test_embed(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"embedding": [0.1, 0.2, 0.3]}

        embedding = self.llm.embed("test")
        self.assertEqual(embedding, [0.1, 0.2, 0.3])

    @patch("sim.llm.llm_ollama.requests.post", side_effect=Exception("API Error"))
    def test_embed_retry_logic(self, mock_post):
        with self.assertRaises(Exception):
            self.llm.embed("test")

if __name__ == "__main__":
    unittest.main()