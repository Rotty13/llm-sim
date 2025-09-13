
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest


@pytest.fixture
def llm():
    from sim.llm.llm_tensorrt import LLM, BELIEF_LOCK_SYSTEM
    return LLM()

def test_chat_basic(llm):
    from sim.llm.llm_tensorrt import BELIEF_LOCK_SYSTEM
    prompt = "Hello, how are you?"
    response = llm.chat(prompt, system=BELIEF_LOCK_SYSTEM, max_tokens=16)
    assert isinstance(response, str)
    assert len(response) > 0

def nottest_embed(llm):
    from sim.llm.llm_tensorrt import  BELIEF_LOCK_SYSTEM
    text = "Test embedding"
    embedding = llm.embed(text)
    assert isinstance(embedding, list)
    assert len(embedding) == 64
    assert all(isinstance(x, float) for x in embedding)

if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main([__file__]))
