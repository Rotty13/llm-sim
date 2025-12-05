import random
from unittest.mock import patch
from tests.utils.scenario_runner import load_scenario
from sim.agents.decision_controller import DecisionController

def test_agent_decision_deterministic():
    world, agents = load_scenario('tests/scenarios/sample_agent_scenario.yaml')
    agent = agents[0]
    controller = DecisionController()
    # Force random to always return 0.99 (should avoid probabilistic branches)
    with patch('random.random', return_value=0.99):
        result = controller.decide(agent, world, '', 0, None)
        # Should fall through to default/THINK or deterministic branch
        assert result['action'] in {'THINK', 'EAT', 'SLEEP', 'RELAX', 'EXPLORE', 'WORK', 'SAY', 'MOVE'}


def test_agent_decision_probabilistic_distribution():
    world, agents = load_scenario('tests/scenarios/sample_agent_scenario.yaml')
    agent = agents[0]
    controller = DecisionController()
    random.seed(42)
    counts = {}
    for _ in range(1000):
        result = controller.decide(agent, world, '', 0, None)
        action = result['action']
        counts[action] = counts.get(action, 0) + 1
    # Example: EXPLORE should occur with reasonable frequency
    assert counts.get('EXPLORE', 0) > 100
    # THINK should also occur
    assert counts.get('THINK', 0) > 100
    # Optionally print counts for debugging
    print('Action distribution:', counts)
