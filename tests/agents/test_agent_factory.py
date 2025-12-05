"""
Pytest-based tests for AgentFactory and agent creation with configurable modules.
"""
import pytest
from sim.agents.agent_factory import AgentFactory
from sim.agents.agents import Persona

@pytest.fixture
def persona():
    return Persona(
        name="Alice",
        age=28,
        job="developer",
        city="TestCity",
        bio="Bio",
        values=["curiosity"],
        goals=["build software"],
        traits={"openness": 0.8},
        aspirations=["exploration"],
        emotional_modifiers={},
        age_transitions={},
        life_stage="adult"
    )

def test_create_agent_with_all_modules(persona):
    agent = AgentFactory.create_agent(persona, place="Office")
    assert agent is not None
    assert agent.memory is not None
    assert agent.inventory is not None
    assert agent.physio is not None

def test_create_agent_with_disabled_modules(persona):
    config = {"memory": False, "inventory": False, "physio": False}
    agent = AgentFactory.create_agent(persona, place="Office", config=config)
    assert agent is not None
    assert agent.memory is None
    assert agent.inventory is None
    assert agent.physio is None
