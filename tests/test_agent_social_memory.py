"""
test_agent_social_memory.py

Automated tests for agent social memory and relationship expansion.
"""
import pytest
from sim.agents.modules.agent_memory import AgentMemory
from sim.agents.modules.agent_social import AgentSocial

@pytest.fixture
def agent_memory():
    return AgentMemory()

@pytest.fixture
def agent_social():
    return AgentSocial()

def test_add_and_retrieve_social_interaction(agent_memory):
    agent_memory.add_social_interaction("Bob", "Greeted at the park")
    agent_memory.add_social_interaction("Alice", "Shared a meal")
    interactions = agent_memory.get_social_interactions()
    assert len(interactions) == 2
    assert interactions[0]["agent_id"] == "Bob"
    assert interactions[1]["agent_id"] == "Alice"

def test_filter_social_interactions_by_agent(agent_memory):
    agent_memory.add_social_interaction("Bob", "Greeted at the park")
    agent_memory.add_social_interaction("Alice", "Shared a meal")
    filtered = agent_memory.get_social_interactions("Bob")
    assert len(filtered) == 1
    assert filtered[0]["interaction"] == "Greeted at the park"

def test_search_social_memory(agent_memory):
    agent_memory.add_social_interaction("Bob", "Greeted at the park")
    agent_memory.add_social_interaction("Alice", "Shared a meal")
    results = agent_memory.search_social_memory("meal")
    assert len(results) == 1
    assert results[0]["agent_id"] == "Alice"

def test_update_affinity(agent_social):
    agent_social.add_connection("Bob", "friend")
    agent_social.update_affinity("Bob", 0.3)
    assert agent_social.connections["Bob"]["affinity"] == 0.3
    agent_social.update_affinity("Bob", 0.8)
    assert agent_social.connections["Bob"]["affinity"] == 1.0

def test_update_rivalry(agent_social):
    agent_social.add_connection("Alice", "rival")
    agent_social.update_rivalry("Alice", 0.5)
    assert agent_social.connections["Alice"]["rivalry"] == 0.5
    agent_social.update_rivalry("Alice", 0.7)
    assert agent_social.connections["Alice"]["rivalry"] == 1.0

def test_update_influence(agent_social):
    agent_social.add_connection("Charlie", "colleague")
    agent_social.update_influence("Charlie", 0.4)
    assert agent_social.connections["Charlie"]["influence"] == 0.4
    agent_social.update_influence("Charlie", 0.7)
    assert agent_social.connections["Charlie"]["influence"] == 1.0
