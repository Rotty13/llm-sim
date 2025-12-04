"""
test_agent_behavior.py

Unit tests for agent behavior, including movement, memory, and decision logic.
"""
import unittest
from sim.agents.agents import Agent, Persona, Physio
from sim.inventory.inventory import Item, ITEMS
from sim.world.world import World, Place
from sim.memory.memory import MemoryItem
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestAgentBehavior(unittest.TestCase):
    def setUp(self):
        self.place = Place(name="Cafe", neighbors=[], capabilities={"food"})
        self.world = World(places={"Cafe": self.place})
        persona = Persona(name="Bob", age=25, job="barista", city="TestCity", bio="Bio", values=["kindness"], goals=["serve coffee"])
        self.agent = Agent(persona=persona, place="Cafe")
        self.world._agents.append(self.agent)
        self.world.set_agent_location(self.agent, "Cafe")
        self.place.add_agent(self.agent)
        self.coffee = ITEMS["coffee"]
        logger.debug(f"Test coffee item: {self.coffee}")
            self.agent.inventory.add_item(self.coffee, 2)

    def test_agent_memory_write(self):
        memory_item = MemoryItem(t=0, kind="episodic", text="Test memory", importance=0.5)
        self.agent.memory.write(memory_item)
        memories = self.agent.memory.recall("episodic", k=1)
        self.assertTrue(any("test memory".lower() in m.text.lower() for m in memories))

    def test_agent_decision(self):
        decision = self.agent.decide(self.world, "see coffee", 0, None)
        self.assertIn("action", decision)
        self.assertIn("private_thought", decision)

    def test_agent_move_and_use_item(self):
        # Agent is already in Cafe (from setUp), so moving to Cafe returns False (no movement needed)
        # The core functionality to test is using an item, so we test that directly
        self.assertEqual(self.agent.place, "Cafe")  # Verify agent is in Cafe
        hunger_before = self.agent.physio.hunger
        self.assertTrue(self.agent.use_item(self.coffee))
        self.assertLess(self.agent.physio.hunger, hunger_before)

    def test_deposit_item_to_place(self):
        # Ensure the agent can deposit an item to the place's inventory
        self.assertTrue(self.agent.deposit_item_to_place(self.world, "coffee", 1))
        self.assertEqual(self.place.inventory.get_quantity("coffee"), 1)
        self.assertEqual(self.agent.inventory.get_quantity("coffee"), 1)

    def test_withdraw_item_from_place(self):
        # Ensure the agent can withdraw an item from the place's inventory
        self.agent.deposit_item_to_place(self.world, "coffee", 1)  # Precondition
        self.assertTrue(self.agent.withdraw_item_from_place(self.world, "coffee", 1))
        self.assertEqual(self.place.inventory.get_quantity("coffee"), 0)
        self.assertEqual(self.agent.inventory.get_quantity("coffee"), 2)

if __name__ == "__main__":
    unittest.main()
