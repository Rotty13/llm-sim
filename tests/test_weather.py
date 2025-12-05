"""
test_weather.py

Unit tests for the Dynamic Weather System (WeatherManager) in llm-sim.
Tests weather transitions, agent hook delegation, and basic mood/physio effects.
"""
import pytest
from sim.world.weather import WeatherManager


class DummyAgent:
    def __init__(self):
        self.weather_received = []
        self.mood_delta = 0.0
        self.energy_delta = 0.0
    def on_weather_update(self, weather_state):
        effects = WeatherManager()._get_weather_effects(weather_state)
        self.weather_received.append(weather_state)
        self.mood_delta += effects.get("mood_boost", 0.0)
        self.energy_delta += effects.get("energy", 0.0)


def test_weather_transitions():
    wm = WeatherManager()
    states = set()
    for _ in range(100):
        wm.update_weather()
        states.add(wm.get_current_weather())
    assert len(states) > 1, "Weather should transition between states."

def test_agent_hook_delegation():
    wm = WeatherManager()
    agent = DummyAgent()
    wm.register_agent_hook(agent.on_weather_update)
    for _ in range(10):
        wm.update_weather()
    assert len(agent.weather_received) == 10
    assert agent.mood_delta != 0.0
    assert agent.energy_delta != 0.0
