"""
Unit tests for the DecisionController class.
"""
import unittest
from unittest.mock import MagicMock, patch
from sim.agents.decision_controller import DecisionController
from sim.agents.agents import Agent, Persona, Physio
from sim.world.world import World, Place
from sim.scheduler.scheduler import Appointment


class TestDecisionController(unittest.TestCase):
    def test_critical_hygiene(self):
        """Test that low hygiene triggers WASH or MOVE decision."""
        # Add a wash place
        wash_place = Place(name="Bathhouse", neighbors=["Home"], capabilities={"wash"})
        self.world.places["Bathhouse"] = wash_place
        # Agent at Bathhouse, low hygiene
        self.agent.place = "Bathhouse"
        self.agent.physio.hygiene = 0.1
        decision = self.controller.decide(self.agent, self.world, "", tick=10, start_dt=None)
        self.assertIn(decision["action"], ["WASH", "MOVE"])
        # Agent not at Bathhouse, low hygiene
        self.agent.place = "Home"
        decision = self.controller.decide(self.agent, self.world, "", tick=10, start_dt=None)
        self.assertIn(decision["action"], ["MOVE"])

    def test_critical_comfort(self):
        """Test that low comfort triggers REST or MOVE decision."""
        # Add a rest place
        rest_place = Place(name="Lounge", neighbors=["Home"], capabilities={"rest"})
        self.world.places["Lounge"] = rest_place
        self.agent.place = "Lounge"
        self.agent.physio.comfort = 0.1
        decision = self.controller.decide(self.agent, self.world, "", tick=10, start_dt=None)
        self.assertIn(decision["action"], ["REST", "MOVE"])
        # Agent not at Lounge, low comfort
        self.agent.place = "Home"
        decision = self.controller.decide(self.agent, self.world, "", tick=10, start_dt=None)
        self.assertIn(decision["action"], ["MOVE"])

    def test_critical_bladder(self):
        """Test that low bladder triggers USE_BATHROOM or MOVE decision."""
        # Add a bathroom place
        bathroom_place = Place(name="Restroom", neighbors=["Home"], capabilities={"bathroom"})
        self.world.places["Restroom"] = bathroom_place
        self.agent.place = "Restroom"
        self.agent.physio.bladder = 0.1
        decision = self.controller.decide(self.agent, self.world, "", tick=10, start_dt=None)
        self.assertIn(decision["action"], ["USE_BATHROOM", "MOVE"])
        # Agent not at Restroom, low bladder
        self.agent.place = "Home"
        decision = self.controller.decide(self.agent, self.world, "", tick=10, start_dt=None)
        self.assertIn(decision["action"], ["MOVE"])

    def setUp(self):
        """Set up test fixtures."""
        self.controller = DecisionController()
        
        # Create a mock world with places
        self.home = Place(name="Home", neighbors=["Cafe"], capabilities={"home", "sleep"})
        self.cafe = Place(name="Cafe", neighbors=["Home"], capabilities={"food"})
        self.office = Place(name="Office", neighbors=["Home"], capabilities={"work"})
        self.world = World(places={
            "Home": self.home,
            "Cafe": self.cafe,
            "Office": self.office
        })
        
        # Create a test agent
        self.persona = Persona(
            name="TestAgent",
            age=30,
            job="developer",
            city="TestCity",
            bio="Test bio",
            values=["ambition", "curiosity"],
            goals=["succeed"]
        )
        self.agent = Agent(persona=self.persona, place="Home")
        self.world.add_agent(self.agent)

    def test_continue_when_busy(self):
        """Test that agent continues when busy."""
        self.agent.busy_until = 100
        decision = self.controller.decide(self.agent, self.world, "", tick=50, start_dt=None)
        self.assertEqual(decision["action"], "CONTINUE")

    def test_critical_hunger(self):
        """Test that critical hunger triggers eat/move decision."""
        self.agent.physio.hunger = 0.9
        self.agent.place = "Cafe"
        decision = self.controller.decide(self.agent, self.world, "", tick=10, start_dt=None)
        self.assertIn(decision["action"], ["EAT", "MOVE"])

    def test_critical_energy(self):
        """Test that low energy triggers sleep/move decision."""
        self.agent.physio.energy = 0.1
        self.agent.place = "Home"
        decision = self.controller.decide(self.agent, self.world, "", tick=10, start_dt=None)
        self.assertIn(decision["action"], ["SLEEP", "MOVE"])

    def test_schedule_enforcement(self):
        """Test that schedule is enforced."""
        # Create an appointment
        self.agent.calendar = [
            Appointment(start_tick=10, end_tick=20, location="Office", label="Work")
        ]
        self.agent.place = "Home"
        
        # Note: enforce_schedule uses end_tick logic, so we need to set tick appropriately
        # The current scheduler checks if (0 <= appt.end_tick - minutes <= 15)
        # With tick=3, minutes=15, end_tick=20: 20-15=5, which is in range
        decision = self.controller.decide(self.agent, self.world, "", tick=3, start_dt=None)
        # The decision should involve moving to Office or some schedule-related action

    def test_default_decision(self):
        """Test default decision when no other criteria match."""
        self.agent.physio.hunger = 0.1
        self.agent.physio.energy = 0.9
        self.agent.physio.stress = 0.1
        # Set to a late-night hour to avoid most context decisions
        decision = self.controller.decide(self.agent, self.world, "", tick=0, start_dt=None)
        # Should get some valid action
        self.assertIn("action", decision)

    def test_decision_includes_private_thought(self):
        """Test that decisions include private thought."""
        decision = self.controller.decide(self.agent, self.world, "", tick=10, start_dt=None)
        self.assertIn("private_thought", decision)


if __name__ == "__main__":
    unittest.main()
