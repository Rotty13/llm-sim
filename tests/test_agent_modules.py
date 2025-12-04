"""
Pytest-based tests for individual agent modules: memory, inventory, mood, actions, social, serialization, relationships.
"""
import pytest
from sim.agents.agents import Agent, Persona
from sim.agents.modules.agent_memory import AgentMemory
from sim.agents.modules.agent_inventory import AgentInventory
from sim.agents.modules.agent_mood import AgentMood
from sim.agents.modules.agent_actions import AgentActions
from sim.agents.modules.agent_social import AgentSocial
from sim.agents.modules.agent_serialization import AgentSerialization
from sim.agents.modules.agent_relationships import AgentRelationships

@pytest.fixture
def agent():
    persona = Persona(
        name="TestAgent",
        age=30,
        job="developer",
        city="TestCity",
        bio="Test bio",
        values=["curiosity"],
        goals=["explore"],
        traits={"openness": 0.8},
        aspirations=["exploration"],
        emotional_modifiers={},
        age_transitions={},
        life_stage="adult"
    )
    return Agent(persona=persona, place="Office")

def test_memory_module(agent):
    if agent.memory is None:
        pytest.skip("AgentMemory module is disabled.")
    assert isinstance(agent.memory, AgentMemory)
    agent.memory.add_episodic("Test memory event")
    episodic = agent.memory.get_episodic()
    assert "Test memory event" in episodic

def test_inventory_module(agent):
    if agent.inventory is None:
        pytest.skip("AgentInventory module is disabled.")
    assert isinstance(agent.inventory, AgentInventory)
    agent.inventory.add_item("test_item", 1)
    assert agent.inventory.get_quantity("test_item") == 1

def test_mood_module(agent):
    if agent.mood is None:
        pytest.skip("AgentMood module is disabled.")
    assert isinstance(agent.mood, AgentMood)
    agent.mood.set_mood("happy", 1.0)
    assert agent.mood.get_mood("happy") == 1.0

def test_actions_module(agent):
    if agent.actions is None:
        pytest.skip("AgentActions module is disabled.")
    assert isinstance(agent.actions, AgentActions)
    result = agent.actions.execute(agent, "SAY", {}, 0)
    assert result
    last_action = agent.actions.get_last_action()
    assert last_action is not None
    if last_action is not None:
        assert last_action["action"] == "SAY"

def test_social_module(agent):
    if agent.social is None:
        pytest.skip("AgentSocial module is disabled.")
    assert isinstance(agent.social, AgentSocial)
    agent.social.add_connection("Bob", "friend")
    assert agent.social.get_connection("Bob") == "friend"
    agent.social.log_interaction("Bob", "greeted")
    assert ("Bob", "greeted") in agent.social.get_interactions()

def test_serialization_module(agent):
    if agent.serialization is None:
        pytest.skip("AgentSerialization module is disabled.")
    assert isinstance(agent.serialization, AgentSerialization)
    state_json = agent.serialization.serialize(agent)
    assert isinstance(state_json, str)

def test_relationships_module(agent):
    if agent.relationships is None:
        pytest.skip("AgentRelationships module is disabled.")
    assert isinstance(agent.relationships, AgentRelationships)
    agent.relationships.set_relationship("Bob", 0.7, 0.8)
    rel = agent.relationships.get_relationship("Bob")
    assert rel["familiarity"] == 0.7
    assert rel["trust"] == 0.8
