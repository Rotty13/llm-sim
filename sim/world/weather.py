"""
Dynamic Weather System for llm-sim

This module defines the WeatherManager class, which manages weather states, transitions, and updates for the simulation world. Weather effects are intended to influence agent behavior and place capabilities. Agent logic should be delegated via hooks or callbacks whenever possible.

Key Classes:
- WeatherManager: Handles current weather, transitions, and tick-based updates.

LLM Usage: None (hardcoded logic only)

CLI Arguments: None
"""

from typing import List, Dict, Optional
import random

class WeatherManager:
    """
    Manages weather states, transitions, and updates for the simulation world.
    Delegates agent-specific logic via hooks/callbacks.
    """
    DEFAULT_STATES = ["sunny", "rainy", "stormy", "snowy", "foggy"]

    def __init__(self, initial_state: Optional[str] = None, states: Optional[List[str]] = None):
        self.states = states if states else self.DEFAULT_STATES
        self.current_state = initial_state if initial_state else self.states[0]
        self.history = [self.current_state]
        # Delegation hooks: agent/weather response functions
        self.agent_weather_hooks = []  # List of callables(agent, weather_state)

    def register_agent_hook(self, hook):
        """Register a hook for agent weather response."""
        self.agent_weather_hooks.append(hook)

    def update_weather(self):
        """
        Update weather state for the current tick.
        Uses a weighted random transition for more realism.
        Applies basic weather effects to agent hooks (mood/physio stubs).
        """
        next_state = self._choose_next_state()
        self.current_state = next_state
        self.history.append(next_state)
        # Delegate to agent hooks (pass weather effects)
        effects = self._get_weather_effects(next_state)
        for hook in self.agent_weather_hooks:
            hook(next_state)
            # Optionally pass effects to agent modules in future

    def _choose_next_state(self) -> str:
        """
        Choose next weather state using simple weighted logic.
        Sunny is more likely, storms less likely.
        """
        weights = {
            "sunny": 0.5,
            "rainy": 0.2,
            "stormy": 0.05,
            "snowy": 0.15,
            "foggy": 0.1
        }
        states = self.states
        probs = [weights.get(s, 0.1) for s in states]
        total = sum(probs)
        norm_probs = [p / total for p in probs]
        return random.choices(states, weights=norm_probs, k=1)[0]

    def _get_weather_effects(self, state: str) -> Dict[str, float]:
        """
        Return basic weather effects for mood/physio (stub for future expansion).
        """
        effects = {
            "sunny": {"mood_boost": 0.1, "energy": 0.05},
            "rainy": {"mood_boost": -0.05, "energy": -0.02},
            "stormy": {"mood_boost": -0.15, "energy": -0.1},
            "snowy": {"mood_boost": 0.05, "energy": -0.05},
            "foggy": {"mood_boost": -0.02, "energy": -0.01}
        }
        return effects.get(state, {})

    def get_current_weather(self) -> str:
        return self.current_state

    def get_weather_history(self) -> List[str]:
        return self.history

# Example usage (to be integrated with World and Agent logic):
# weather_mgr = WeatherManager()
# weather_mgr.register_agent_hook(agent_weather_response)
# weather_mgr.update_weather()
