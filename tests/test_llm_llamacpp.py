

"""
test_llm_llamacpp.py
Unit test for LlamaCppLLM wrapper.
"""
import os
import pytest
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sim.llm.llm_llamacpp import LlamaCppLLM

MODEL_PATH = os.environ.get("LLAMA_CPP_MODEL_PATH", "llama3.1:8b-instruct-q4_0")

@pytest.mark.skipif(not os.path.exists(MODEL_PATH), reason="Model file not found.")
def test_llamacpp_basic_generation():
    llm = LlamaCppLLM(MODEL_PATH)
    prompt = "Hello, my name is"
    result = llm.generate(prompt, max_tokens=32)
    assert isinstance(result, str)
    assert len(result.strip()) > 0
    print("Model output:", result)



if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
