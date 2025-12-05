"""
Unit tests for the LLM class in llm_ollama.py.
"""
import pytest
from unittest.mock import patch, MagicMock
from sim.llm.llm_ollama import LLM


@pytest.fixture
def llm():
    return LLM()

@patch("sim.llm.llm_ollama.requests.post")
def test_chat(mock_post, llm):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"message": {"content": "Hello!"}}
    response = llm.chat("Hi")
    assert response == "Hello!"

@patch("sim.llm.llm_ollama.requests.post")
def test_chat_json(mock_post, llm):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"message": {"content": '{"key": "value"}'}}
    response = llm.chat_json("Hi")
    assert response == {"key": "value"}

@patch("sim.llm.llm_ollama.requests.post")
def test_embed(mock_post, llm):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
    embedding = llm.embed("test")
    assert embedding == [0.1, 0.2, 0.3]

@patch("sim.llm.llm_ollama.requests.post", side_effect=Exception("API Error"))
def test_embed_retry_logic(mock_post, llm):
    with pytest.raises(Exception):
        llm.embed("test")