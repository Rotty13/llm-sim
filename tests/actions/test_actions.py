"""
Pytest-based tests for the actions module.
"""
import pytest
from sim.actions.actions import (
    normalize_action, parse_action, get_action_duration, 
    get_action_effects, ACTION_DURATIONS, ACTION_COSTS
)

def test_normalize_action_string():
    result = normalize_action("MOVE")
    assert result == "MOVE()"

def test_normalize_action_dict():
    result = normalize_action({"action": "MOVE", "to": "Cafe"})
    assert "MOVE" in result
    assert "Cafe" in result

def test_normalize_action_with_params():
    result = normalize_action('MOVE({"to":"Home"})')
    assert "MOVE" in result

def test_parse_action_simple():
    action_type, params = parse_action("THINK()")
    assert action_type == "THINK"
    assert params == {}

def test_parse_action_with_params():
    action_type, params = parse_action('MOVE({"to":"Cafe"})')
    assert action_type == "MOVE"
    assert params.get("to") == "Cafe"

def test_get_action_duration():
    duration = get_action_duration("SLEEP")
    assert duration == ACTION_DURATIONS["SLEEP"]

def test_get_action_duration_custom():
    duration = get_action_duration("WORK", {"duration": 20})
    assert duration == 20

def test_get_action_effects():
    effects = get_action_effects("EAT")
    assert "hunger" in effects
    assert effects["hunger"] < 0  # Eating reduces hunger

def test_action_durations_defined():
    expected_actions = ["SAY", "MOVE", "INTERACT", "THINK", "SLEEP", "EAT", "WORK", "RELAX", "EXPLORE"]
    for action in expected_actions:
        assert action in ACTION_DURATIONS

def test_action_costs_defined():
    expected_actions = ["SAY", "MOVE", "WORK", "SLEEP", "EAT"]
    for action in expected_actions:
        assert action in ACTION_COSTS
