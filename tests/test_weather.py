"""
test_weather.py

Unit tests for the Dynamic Weather System (WeatherManager) in llm-sim.
Tests weather transitions, agent hook delegation, and basic mood/physio effects.
"""
import unittest
from sim.world.weather import WeatherManager

class DummyAgent:
    def __init__(self):
        self.weather_received = []
        self.mood_delta = 0.0
        self.energy_delta = 0.0
    def on_weather_update(self, weather_state):
        # Simulate mood/energy effect handling
        effects = WeatherManager()._get_weather_effects(weather_state)
        self.weather_received.append(weather_state)
        self.mood_delta += effects.get("mood_boost", 0.0)
        self.energy_delta += effects.get("energy", 0.0)

class TestWeatherManager(unittest.TestCase):
    def test_weather_transitions(self):
        wm = WeatherManager()
        states = set()
        for _ in range(100):
            wm.update_weather()
            states.add(wm.get_current_weather())
        self.assertTrue(len(states) > 1, "Weather should transition between states.")

    def test_agent_hook_delegation(self):
        wm = WeatherManager()
        agent = DummyAgent()
        wm.register_agent_hook(agent.on_weather_update)
        for _ in range(10):
            wm.update_weather()
        self.assertEqual(len(agent.weather_received), 10)
        # Check that mood/energy deltas are being updated
        self.assertNotEqual(agent.mood_delta, 0.0)
        self.assertNotEqual(agent.energy_delta, 0.0)

if __name__ == "__main__":
    unittest.main()
