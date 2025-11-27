"""
test_simulation_scenarios.py

Scenario and integration tests for llm-sim simulation engine.
Covers agent movement, item transfer, and basic world interactions.
"""
import unittest
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
from sim.world.world import World, Place
from sim.agents.agents import Agent, Persona, Physio
from sim.inventory.inventory import Item

class TestSimulationScenarios(unittest.TestCase):
    def setUp(self):
        # Create simple world with two places
        self.place_a = Place(name="Cafe", neighbors=["Office"], capabilities={"food"})
        self.place_b = Place(name="Office", neighbors=["Cafe"], capabilities={"work_dev"})
        self.world = World(places={"Cafe": self.place_a, "Office": self.place_b})
        # Create agent
        persona = Persona(name="Alice", age=30, job="developer", city="TestCity", bio="Test bio", values=["honesty"], goals=["finish project"])
        self.agent = Agent(persona=persona, place="Cafe")
        self.world._agents.append(self.agent)
        self.world.set_agent_location(self.agent, "Cafe")
        self.place_a.add_agent(self.agent)
        # Create item
        self.coffee = Item(id="coffee", name="Coffee", tags={"food"}, weight=0.2, effects={"hunger": -0.1})
        self.agent.inventory.add(self.coffee, 1)

    def test_agent_move(self):
        self.assertTrue(self.agent.move_to(self.world, "Office"))
        self.assertEqual(self.agent.place, "Office")
        self.assertIn(self.agent, self.place_b.agents_present)
        self.assertNotIn(self.agent, self.place_a.agents_present)

    def test_item_transfer(self):
        # Agent transfers coffee to Office
        self.assertTrue(self.world.transfer_item(self.agent, self.place_b, "coffee", 1))
        self.assertFalse(self.agent.inventory.has("coffee"))
        self.assertTrue(self.place_b.inventory.has("coffee"))

    def test_agent_use_item(self):
        # Agent uses coffee
        self.agent.inventory.add(self.coffee, 1)
        hunger_before = self.agent.physio.hunger
        self.assertTrue(self.agent.use_item(self.coffee))
        self.assertLess(self.agent.physio.hunger, hunger_before)

if __name__ == "__main__":
    unittest.main()
