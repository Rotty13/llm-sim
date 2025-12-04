"""
test_agent_modules.py

Unit tests for individual agent modules: memory, inventory, mood, actions, social, serialization, relationships.
"""
import unittest
from sim.agents.agents import Agent, Persona
from sim.agents.modules.agent_memory import AgentMemory
from sim.agents.modules.agent_inventory import AgentInventory
from sim.agents.modules.agent_mood import AgentMood
from sim.agents.modules.agent_actions import AgentActions
from sim.agents.modules.agent_social import AgentSocial
from sim.agents.modules.agent_serialization import AgentSerialization
from sim.agents.modules.agent_relationships import AgentRelationships

class TestAgentModules(unittest.TestCase):
    def setUp(self):
        self.persona = Persona(
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
        self.agent = Agent(persona=self.persona, place="Office")

    def test_memory_module(self):
        if self.agent.memory is None:
            self.skipTest("AgentMemory module is disabled.")
        self.assertIsInstance(self.agent.memory, AgentMemory)
        self.agent.memory.add_episodic("Test memory event")
        episodic = self.agent.memory.get_episodic()
        self.assertIn("Test memory event", episodic)

    def test_inventory_module(self):
        if self.agent.inventory is None:
            self.skipTest("AgentInventory module is disabled.")
        self.assertIsInstance(self.agent.inventory, AgentInventory)
        self.agent.inventory.add_item("test_item", 1)
        self.assertEqual(self.agent.inventory.get_quantity("test_item"), 1)

    def test_mood_module(self):
        if self.agent.mood is None:
            self.skipTest("AgentMood module is disabled.")
        self.assertIsInstance(self.agent.mood, AgentMood)
        self.agent.mood.set_mood("happy", 1.0)
        self.assertEqual(self.agent.mood.get_mood("happy"), 1.0)

    def test_actions_module(self):
        if self.agent.actions is None:
            self.skipTest("AgentActions module is disabled.")
        self.assertIsInstance(self.agent.actions, AgentActions)
        result = self.agent.actions.perform_action("SAY")
        self.assertEqual(result, "Action performed: SAY")
        self.assertEqual(self.agent.actions.get_last_action(), "SAY")

    def test_social_module(self):
        if self.agent.social is None:
            self.skipTest("AgentSocial module is disabled.")
        self.assertIsInstance(self.agent.social, AgentSocial)
        self.agent.social.add_connection("Bob", "friend")
        self.assertEqual(self.agent.social.get_connection("Bob"), "friend")
        self.agent.social.log_interaction("Bob", "greeted")
        self.assertIn(("Bob", "greeted"), self.agent.social.get_interactions())

    def test_serialization_module(self):
        if self.agent.serialization is None:
            self.skipTest("AgentSerialization module is disabled.")
        self.assertIsInstance(self.agent.serialization, AgentSerialization)
        state_json = self.agent.serialization.serialize(self.agent)
        self.assertIsInstance(state_json, str)

    def test_relationships_module(self):
        if self.agent.relationships is None:
            self.skipTest("AgentRelationships module is disabled.")
        self.assertIsInstance(self.agent.relationships, AgentRelationships)
        self.agent.relationships.set_relationship("Bob", 0.7, 0.8)
        rel = self.agent.relationships.get_relationship("Bob")
        self.assertEqual(rel["familiarity"], 0.7)
        self.assertEqual(rel["trust"], 0.8)

if __name__ == "__main__":
    unittest.main()
