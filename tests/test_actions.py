"""
Unit tests for the actions module.
"""
import unittest
from sim.actions.actions import (
    normalize_action, parse_action, get_action_duration, 
    get_action_effects, ACTION_DURATIONS, ACTION_COSTS
)


class TestActions(unittest.TestCase):

    def test_normalize_action_string(self):
        """Test normalizing a simple action string."""
        result = normalize_action("MOVE")
        self.assertEqual(result, "MOVE()")

    def test_normalize_action_dict(self):
        """Test normalizing a dict action."""
        result = normalize_action({"action": "MOVE", "to": "Cafe"})
        self.assertIn("MOVE", result)
        self.assertIn("Cafe", result)

    def test_normalize_action_with_params(self):
        """Test normalizing action with parameters."""
        result = normalize_action('MOVE({"to":"Home"})')
        self.assertIn("MOVE", result)

    def test_parse_action_simple(self):
        """Test parsing a simple action."""
        action_type, params = parse_action("THINK()")
        self.assertEqual(action_type, "THINK")
        self.assertEqual(params, {})

    def test_parse_action_with_params(self):
        """Test parsing action with parameters."""
        action_type, params = parse_action('MOVE({"to":"Cafe"})')
        self.assertEqual(action_type, "MOVE")
        self.assertEqual(params.get("to"), "Cafe")

    def test_get_action_duration(self):
        """Test getting action duration."""
        duration = get_action_duration("SLEEP")
        self.assertEqual(duration, ACTION_DURATIONS["SLEEP"])

    def test_get_action_duration_custom(self):
        """Test getting custom action duration from params."""
        duration = get_action_duration("WORK", {"duration": 20})
        self.assertEqual(duration, 20)

    def test_get_action_effects(self):
        """Test getting action effects."""
        effects = get_action_effects("EAT")
        self.assertIn("hunger", effects)
        self.assertLess(effects["hunger"], 0)  # Eating reduces hunger

    def test_action_durations_defined(self):
        """Test that all expected actions have durations."""
        expected_actions = ["SAY", "MOVE", "INTERACT", "THINK", "SLEEP", "EAT", "WORK", "RELAX", "EXPLORE"]
        for action in expected_actions:
            self.assertIn(action, ACTION_DURATIONS)

    def test_action_costs_defined(self):
        """Test that all expected actions have costs."""
        expected_actions = ["SAY", "MOVE", "WORK", "SLEEP", "EAT"]
        for action in expected_actions:
            self.assertIn(action, ACTION_COSTS)


if __name__ == "__main__":
    unittest.main()
