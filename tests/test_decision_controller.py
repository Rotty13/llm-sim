"""
Pytest-based tests for the DecisionController class.
"""
import pytest
from sim.agents.decision_controller import DecisionController
from sim.agents.agents import Agent, Persona, Physio
from sim.world.world import World, Place
from sim.scheduler.scheduler import Appointment

@pytest.fixture
def controller_and_agent():
    controller = DecisionController()
    # Create a mock world with places
    home = Place(name="Home", neighbors=["Cafe"], capabilities={"home", "sleep"})
    cafe = Place(name="Cafe", neighbors=["Home"], capabilities={"food"})
    office = Place(name="Office", neighbors=["Home"], capabilities={"work"})
    world = World(places={
        "Home": home,
        "Cafe": cafe,
        "Office": office
    })
    persona = Persona(
        name="TestAgent",
        age=30,
        job="developer",
        city="TestCity",
        bio="Test bio",
        values=["ambition", "curiosity"],
        goals=["succeed"]
    )
    agent = Agent(persona=persona, place="Home")
    world.add_agent(agent)
    return controller, agent, world

def test_critical_hygiene(controller_and_agent):
    controller, agent, world = controller_and_agent
    wash_place = Place(name="Bathhouse", neighbors=["Home"], capabilities={"wash"})
    world.places["Bathhouse"] = wash_place
    agent.place = "Bathhouse"
    if agent.physio is not None:
        agent.physio.hygiene = 0.1
    decision = controller.decide(agent, world, "", tick=10, start_dt=None)
    assert decision["action"] in ["WASH", "MOVE"]
    agent.place = "Home"
    decision = controller.decide(agent, world, "", tick=10, start_dt=None)
    assert decision["action"] in ["MOVE"]

def test_critical_comfort(controller_and_agent):
    controller, agent, world = controller_and_agent
    rest_place = Place(name="Lounge", neighbors=["Home"], capabilities={"rest"})
    world.places["Lounge"] = rest_place
    agent.place = "Lounge"
    if agent.physio is not None:
        agent.physio.comfort = 0.1
    decision = controller.decide(agent, world, "", tick=10, start_dt=None)
    assert decision["action"] in ["REST", "MOVE"]
    agent.place = "Home"
    decision = controller.decide(agent, world, "", tick=10, start_dt=None)
    assert decision["action"] in ["MOVE"]

def test_critical_bladder(controller_and_agent):
    controller, agent, world = controller_and_agent
    bathroom_place = Place(name="Restroom", neighbors=["Home"], capabilities={"bathroom"})
    world.places["Restroom"] = bathroom_place
    agent.place = "Restroom"
    if agent.physio is not None:
        agent.physio.bladder = 0.1
    decision = controller.decide(agent, world, "", tick=10, start_dt=None)
    assert decision["action"] in ["USE_BATHROOM", "MOVE"]
    agent.place = "Home"
    decision = controller.decide(agent, world, "", tick=10, start_dt=None)
    assert decision["action"] in ["MOVE"]

def test_continue_when_busy(controller_and_agent):
    controller, agent, world = controller_and_agent
    agent.busy_until = 100
    decision = controller.decide(agent, world, "", tick=50, start_dt=None)
    assert decision["action"] == "CONTINUE"

def test_critical_hunger(controller_and_agent):
    controller, agent, world = controller_and_agent
    if agent.physio is not None:
        agent.physio.hunger = 0.9
    agent.place = "Cafe"
    decision = controller.decide(agent, world, "", tick=10, start_dt=None)
    assert decision["action"] in ["EAT", "MOVE"]

def test_critical_energy(controller_and_agent):
    controller, agent, world = controller_and_agent
    if agent.physio is not None:
        agent.physio.energy = 0.1
    agent.place = "Home"
    decision = controller.decide(agent, world, "", tick=10, start_dt=None)
    assert decision["action"] in ["SLEEP", "MOVE"]

def test_schedule_enforcement(controller_and_agent):
    controller, agent, world = controller_and_agent
    agent.calendar = [
        Appointment(start_tick=10, end_tick=20, location="Office", label="Work")
    ]
    agent.place = "Home"
    decision = controller.decide(agent, world, "", tick=3, start_dt=None)
    # The decision should involve moving to Office or some schedule-related action
    assert decision is not None

def test_default_decision(controller_and_agent):
    controller, agent, world = controller_and_agent
    if agent.physio is not None:
        agent.physio.hunger = 0.1
        agent.physio.energy = 0.9
        agent.physio.stress = 0.1
    decision = controller.decide(agent, world, "", tick=0, start_dt=None)
    assert "action" in decision

def test_decision_includes_private_thought(controller_and_agent):
    controller, agent, world = controller_and_agent
    decision = controller.decide(agent, world, "", tick=10, start_dt=None)
    assert "private_thought" in decision
