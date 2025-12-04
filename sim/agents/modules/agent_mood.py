"""
AgentMood module for managing agent mood state and transitions.
Handles mood initialization, updates, and mood-related queries.
"""

class AgentMood:
    def __init__(self, initial_mood=None):
        self.mood = initial_mood or {}

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
