import glob
import pytest
import yaml
from tests.utils.scenario_runner import load_scenario
from sim.agents.decision_controller import DecisionController

tier2_scenarios = glob.glob('tests/scenarios/tier2_intermediate/*.yaml')

@pytest.mark.parametrize("scenario_path", tier2_scenarios)
def test_tier2_scenarios(scenario_path):
    world, agents = load_scenario(scenario_path)
    # For tier 2, test all agents' first decisions
    controller = DecisionController()
    for agent in agents:
        result = controller.decide(agent, world, '', 0, None)
        print(f"\n--- Scenario: {scenario_path} ---\nAgent: {agent.persona.name if hasattr(agent, 'persona') else agent}\nResult: {result}\n")
        # Optionally, check for expected_action in YAML (per agent, if specified)
        with open(scenario_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        # If you want per-agent expected actions, extend YAML and logic here
        assert result['action'] in {'EAT', 'SLEEP', 'RELAX', 'EXPLORE', 'THINK', 'USE_BATHROOM', 'SAY', 'WORK', 'MOVE', 'TRADE'}, f"Unexpected action {result['action']} in {scenario_path} for agent {agent.persona.name}"
