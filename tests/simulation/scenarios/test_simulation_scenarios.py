"""
test_simulation_scenarios.py

Scenario and integration tests for llm-sim simulation engine.
Covers agent movement, item transfer, and basic world interactions.
"""
import pytest
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
from sim.world.world import World, Place
from sim.agents.agents import Agent, Persona, Physio
from sim.inventory.inventory import Item


# Helper functions for setup
def setup_world_and_agent():
    place_a = Place(name="Cafe", neighbors=["Office"], capabilities={"food"})
    place_b = Place(name="Office", neighbors=["Cafe"], capabilities={"work_dev"})
    world = World(places={"Cafe": place_a, "Office": place_b})
    persona = Persona(name="Alice", age=30, job="developer", city="TestCity", bio="Test bio", values=["honesty"], goals=["finish project"])
    agent = Agent(persona=persona, place="Cafe")
    world._agents.append(agent)
    world.set_agent_location(agent, "Cafe")
    place_a.add_agent(agent)
    coffee = Item(id="coffee", name="Coffee", tags={"food"}, weight=0.2, effects={"hunger": -0.1})
    if agent.inventory is not None:
        agent.inventory.add(coffee, 1)
    return world, place_a, place_b, agent, coffee

def setup_agent_bob():
    persona = Persona(
        name="Bob", age=20, job="barista", city="TestCity", bio="Test bio",
        values=["curiosity"], goals=["explore"],
        traits={"openness": 0.9, "conscientiousness": 0.2, "extraversion": 0.8, "agreeableness": 0.5, "neuroticism": 0.3},
        aspirations=["learn"], emotional_modifiers={"baseline_mood": 0.2, "emotional_reactivity": 0.7}
    )
    agent = Agent(persona=persona, place="Cafe")
    if agent.physio is not None:
        agent.physio.hunger = 0.9
        agent.physio.fun = 0.2
        agent.physio.social = 0.2
    return agent

def test_agent_scheduler_loop():
    world, _, _, agent, _ = setup_world_and_agent()
    world.simulation_loop(ticks=5)
    assert agent.alive
    assert agent.place in ["Cafe", "Office"]
    assert isinstance(world.metrics.summary(), dict)

def test_agent_move():
    world, place_a, place_b, agent, _ = setup_world_and_agent()
    assert agent.move_to(world, "Office")
    assert agent.place == "Office"
    assert agent in place_b.agents_present
    assert agent not in place_a.agents_present

def test_item_transfer():
    world, _, place_b, agent, _ = setup_world_and_agent()
    assert world.transfer_item(agent, place_b, "coffee", 1)
    if agent.inventory is not None:
        assert not agent.inventory.has("coffee")
    if hasattr(place_b, 'inventory') and place_b.inventory is not None:
        assert place_b.inventory.has("coffee")

def test_agent_use_item():
    world, _, _, agent, coffee = setup_world_and_agent()
    if agent.inventory is not None:
        agent.inventory.add(coffee, 1)
    if agent.physio is not None:
        hunger_before = agent.physio.hunger
        assert agent.use_item(coffee)
        assert agent.physio.hunger < hunger_before

def test_needs_decay():
    agent = setup_agent_bob()
    if agent.physio is not None:
        hunger_before = agent.physio.hunger
        agent.physio.decay_needs()
        assert agent.physio.hunger > hunger_before

def test_personality_decision():
    agent = setup_agent_bob()
    decision = agent.decide(None, "", 0, None)
    assert decision["action"] in ["EXPLORE", "SAY", "EAT"]

def test_moodlet_emotion():
    agent = setup_agent_bob()
    agent.add_moodlet("happy", 3)
    agent.set_emotional_state("happy")
    agent.tick_moodlets()
    if agent.physio is not None:
        assert "happy" in agent.physio.moodlets
        assert agent.physio.emotional_state == "happy"

def test_life_stage_transition():
    agent = setup_agent_bob()
    agent.persona.age = 70
    agent.update_life_stage()
    assert agent.persona.life_stage == "elder"

# --- Consolidated scenario-based tests from tier1 and tier2 ---
import glob
import yaml
from tests.utils.scenario_runner import load_scenario
from sim.agents.decision_controller import DecisionController

# Tier 1 scenarios
tier1_scenarios = glob.glob('tests/scenarios/tier1_simple/*.yaml')

@pytest.mark.parametrize("scenario_path", tier1_scenarios)
def test_tier1_scenarios(scenario_path):
    world, agents = load_scenario(scenario_path)
    agent = agents[0]
    controller = DecisionController()
    result = controller.decide(agent, world, '', 0, None)
    print(f"\n--- Scenario: {scenario_path} ---\nAgent: {agent.persona.name if hasattr(agent, 'persona') else agent}\nResult: {result}\n")
    with open(scenario_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    expected_action = data.get('expected_action')
    if expected_action:
        assert result['action'] == expected_action, f"Expected {expected_action}, got {result['action']} for {scenario_path}"
    else:
        assert result['action'] in {'EAT', 'SLEEP', 'RELAX', 'EXPLORE', 'THINK', 'USE_BATHROOM', 'SAY', 'WORK', 'MOVE'}, f"Unexpected action {result['action']} in {scenario_path}"

# Tier 2 scenarios
tier2_scenarios = glob.glob('tests/scenarios/tier2_intermediate/*.yaml')

@pytest.mark.parametrize("scenario_path", tier2_scenarios)
def test_tier2_scenarios(scenario_path):
    world, agents = load_scenario(scenario_path)
    controller = DecisionController()
    for agent in agents:
        result = controller.decide(agent, world, '', 0, None)
        print(f"\n--- Scenario: {scenario_path} ---\nAgent: {agent.persona.name if hasattr(agent, 'persona') else agent}\nResult: {result}\n")
        with open(scenario_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert result['action'] in {'EAT', 'SLEEP', 'RELAX', 'EXPLORE', 'THINK', 'USE_BATHROOM', 'SAY', 'WORK', 'MOVE', 'TRADE'}, f"Unexpected action {result['action']} in {scenario_path} for agent {agent.persona.name}"

def test_death_and_consequences():
    agent = setup_agent_bob()
    agent.die(100)
    assert not agent.alive
    assert agent.time_of_death == 100

def test_job_income():
    agent = setup_agent_bob()
    balance_before = agent.money_balance
    agent.receive_income(10)
    assert agent.money_balance > balance_before

def test_relationship_social_memory():
    agent = setup_agent_bob()
    agent.update_relationship("Alice", 0.5)
    agent.remember_social_interaction({"with": "Alice", "type": "talk"})
    if agent.relationships is not None:
        assert "Alice" in agent.relationships
        assert agent.relationships["Alice"] == 0.5
    if agent.social_memory is not None and len(agent.social_memory) > 0:
        assert agent.social_memory[0]["with"] == "Alice"

def test_persistence_stubs():
    agent = setup_agent_bob()
    state = agent.serialize_state()
    agent.load_state(state)
