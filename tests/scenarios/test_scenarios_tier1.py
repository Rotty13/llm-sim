import glob
import pytest
import yaml
from tests.utils.scenario_runner import load_scenario
from sim.agents.decision_controller import DecisionController

def get_expected_action(scenario_path):
    # Optionally, read expected_action from scenario YAML
    with open(scenario_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data.get('expected_action')

# Parametrize over all tier 1 scenarios
tier1_scenarios = glob.glob('tests/scenarios/tier1_simple/*.yaml')

@pytest.mark.parametrize("scenario_path", tier1_scenarios)
def test_tier1_scenarios(scenario_path):
    world, agents = load_scenario(scenario_path)
    agent = agents[0]
    controller = DecisionController()
    result = controller.decide(agent, world, '', 0, None)
    print(f"\n--- Scenario: {scenario_path} ---\nAgent: {agent.persona.name if hasattr(agent, 'persona') else agent}\nResult: {result}\n")
    # If scenario YAML has 'expected_action', assert it
    with open(scenario_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    expected_action = data.get('expected_action')
    if expected_action:
        assert result['action'] == expected_action, f"Expected {expected_action}, got {result['action']} for {scenario_path}"
    else:
        # Otherwise, just check it's a valid action
        assert result['action'] in {'EAT', 'SLEEP', 'RELAX', 'EXPLORE', 'THINK', 'USE_BATHROOM', 'SAY', 'WORK', 'MOVE'}, f"Unexpected action {result['action']} in {scenario_path}"
