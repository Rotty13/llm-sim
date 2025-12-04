"""
AgentMood module for managing agent mood state and transitions.
Handles mood initialization, updates, and mood-related queries.
"""

class AgentMood:
    def __init__(self, initial_mood=None):
        self.mood = initial_mood or {}

    def on_weather_update(self, weather_state: str):
        """
        Update mood based on weather state. Uses basic effect mapping.
        """
        effects = {
            "sunny": 0.1,
            "rainy": -0.05,
            "stormy": -0.15,
            "snowy": 0.05,
            "foggy": -0.02
        }
        delta = effects.get(weather_state, 0.0)
        self.update_mood("weather", delta)

    def set_mood(self, mood_type, value):
        self.mood[mood_type] = value

    def get_mood(self, mood_type):
        return self.mood.get(mood_type)

    def update_mood(self, mood_type, delta):
        if mood_type in self.mood:
            self.mood[mood_type] += delta
        else:
            self.mood[mood_type] = delta

    def all_moods(self):
        return self.mood.copy()
