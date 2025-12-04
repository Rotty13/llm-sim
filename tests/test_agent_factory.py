"""
test_agent_factory.py

Unit tests for AgentFactory and agent creation with configurable modules.
"""
import unittest
from sim.agents.agent_factory import AgentFactory
from sim.agents.agents import Persona

class TestAgentFactory(unittest.TestCase):
    def setUp(self):
        self.persona = Persona(
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

    def test_create_agent_with_all_modules(self):
        agent = AgentFactory.create_agent(self.persona, place="Office")
        self.assertIsNotNone(agent)
        self.assertIsNotNone(agent.memory)
        self.assertIsNotNone(agent.inventory)
        self.assertIsNotNone(agent.physio)

    def test_create_agent_with_disabled_modules(self):
        config = {"memory": False, "inventory": False, "physio": False}
        agent = AgentFactory.create_agent(self.persona, place="Office", config=config)
        self.assertIsNotNone(agent)
        self.assertIsNone(agent.memory)
        self.assertIsNone(agent.inventory)
        self.assertIsNone(agent.physio)

if __name__ == "__main__":
    unittest.main()
