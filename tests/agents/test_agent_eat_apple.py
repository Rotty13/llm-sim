from tests.utils.scenario_runner import load_scenario
from sim.agents.decision_controller import DecisionController

def test_agent_eats_apple_in_kitchen():
    world, agents = load_scenario('tests/scenarios/tier1_simple/eat_apple_scenario.yaml')
    agent = agents[0]
    controller = DecisionController()
    result = controller.decide(agent, world, '', 0, None)
    assert result['action'] == 'EAT', f"Expected action 'EAT', got {result['action']}"
    # Optionally check that the apple is present in the kitchen before the action
    kitchen = world.places['Kitchen']
    assert kitchen.inventory.has('apple'), "Apple should be present in the kitchen inventory before eating."
