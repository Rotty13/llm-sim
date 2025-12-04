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
        if self.agent.inventory is not None:
            self.agent.inventory.add(self.coffee, 1)

    def test_agent_scheduler_loop(self):
        # Run the simulation loop for 5 ticks
        self.world.simulation_loop(ticks=5)
        # After loop, agent should still be alive and in a valid place
        self.assertTrue(self.agent.alive)
        self.assertIn(self.agent.place, ["Cafe", "Office"])
        # Optionally check metrics or other state changes
        self.assertIsInstance(self.world.metrics.summary(), dict)

    def test_agent_move(self):
        self.assertTrue(self.agent.move_to(self.world, "Office"))
        self.assertEqual(self.agent.place, "Office")
        self.assertIn(self.agent, self.place_b.agents_present)
        self.assertNotIn(self.agent, self.place_a.agents_present)

    def test_item_transfer(self):
        # Agent transfers coffee to Office
        self.assertTrue(self.world.transfer_item(self.agent, self.place_b, "coffee", 1))
        if self.agent.inventory is not None:
            self.assertFalse(self.agent.inventory.has("coffee"))
        if hasattr(self.place_b, 'inventory') and self.place_b.inventory is not None:
            self.assertTrue(self.place_b.inventory.has("coffee"))

    def test_agent_use_item(self):
        # Agent uses coffee
        if self.agent.inventory is not None:
            self.agent.inventory.add(self.coffee, 1)
        if self.agent.physio is not None:
            hunger_before = self.agent.physio.hunger
            self.assertTrue(self.agent.use_item(self.coffee))
            self.assertLess(self.agent.physio.hunger, hunger_before)

class TestAgentIntegrationSkeleton(unittest.TestCase):
    def setUp(self):
        # Minimal agent and world setup
        persona = Persona(
            name="Bob", age=20, job="barista", city="TestCity", bio="Test bio",
            values=["curiosity"], goals=["explore"],
            traits={"openness": 0.9, "conscientiousness": 0.2, "extraversion": 0.8, "agreeableness": 0.5, "neuroticism": 0.3},
            aspirations=["learn"], emotional_modifiers={"baseline_mood": 0.2, "emotional_reactivity": 0.7}
        )
        self.agent = Agent(persona=persona, place="Cafe")
        if self.agent.physio is not None:
            self.agent.physio.hunger = 0.9
            self.agent.physio.fun = 0.2
            self.agent.physio.social = 0.2

    def test_needs_decay(self):
        if self.agent.physio is not None:
            hunger_before = self.agent.physio.hunger
            self.agent.physio.decay_needs()
            self.assertGreater(self.agent.physio.hunger, hunger_before)

    def test_personality_decision(self):
        # Openness and extraversion should bias toward EXPLORE or SAY
        decision = self.agent.decide(None, "", 0, None)
        self.assertIn(decision["action"], ["EXPLORE", "SAY", "EAT"])

    def test_moodlet_emotion(self):
        self.agent.add_moodlet("happy", 3)
        self.agent.set_emotional_state("happy")
        self.agent.tick_moodlets()
        if self.agent.physio is not None:
            self.assertIn("happy", self.agent.physio.moodlets)
            self.assertEqual(self.agent.physio.emotional_state, "happy")

    def test_life_stage_transition(self):
        self.agent.persona.age = 70
        self.agent.update_life_stage()
        self.assertEqual(self.agent.persona.life_stage, "elder")

    def test_death_and_consequences(self):
        self.agent.die(100)
        self.assertFalse(self.agent.alive)
        self.assertEqual(self.agent.time_of_death, 100)

    def test_job_income(self):
        balance_before = self.agent.money_balance
        self.agent.receive_income(10)
        self.assertGreater(self.agent.money_balance, balance_before)

    def test_relationship_social_memory(self):
        self.agent.update_relationship("Alice", 0.5)
        self.agent.remember_social_interaction({"with": "Alice", "type": "talk"})
        if self.agent.relationships is not None:
            self.assertIn("Alice", self.agent.relationships)
            self.assertEqual(self.agent.relationships["Alice"], 0.5)
        if self.agent.social_memory is not None and len(self.agent.social_memory) > 0:
            self.assertEqual(self.agent.social_memory[0]["with"], "Alice")

    def test_persistence_stubs(self):
        state = self.agent.serialize_state()
        self.agent.load_state(state)
        # Removed call to nonexistent checkpoint_stub method


if __name__ == "__main__":
    unittest.main()
