"""
AgentPhysio module for managing agent physiological state and moodlets.
Handles needs decay, moodlet triggers, and moodlet ticking.
"""

class AgentPhysio:
    def get_life_stage_modifiers(self, agent):
        """Return physiological modifiers based on agent's life stage."""
        stage = getattr(agent.persona, 'life_stage', 'adult')
        # Example: hunger decay, energy decay, stress sensitivity, etc.
        modifiers = {
            'infant':    {'hunger_decay': 1.5, 'energy_decay': 2.0, 'stress_sensitivity': 1.2},
            'toddler':   {'hunger_decay': 1.3, 'energy_decay': 1.7, 'stress_sensitivity': 1.1},
            'child':     {'hunger_decay': 1.1, 'energy_decay': 1.3, 'stress_sensitivity': 1.0},
            'teen':      {'hunger_decay': 1.0, 'energy_decay': 1.1, 'stress_sensitivity': 1.0},
            'young adult': {'hunger_decay': 1.0, 'energy_decay': 1.0, 'stress_sensitivity': 1.0},
            'adult':     {'hunger_decay': 1.0, 'energy_decay': 1.0, 'stress_sensitivity': 1.0},
            'elder':     {'hunger_decay': 0.9, 'energy_decay': 0.8, 'stress_sensitivity': 1.3},
        }
        return modifiers.get(stage, modifiers['adult'])
    def __init__(self, physio=None):
        self.physio = physio

    def set_emotional_state(self, state: str):
        """Set the agent's current emotional state."""
        if self.physio:
            self.physio.emotional_state = state

    def set_mood(self, mood: str):
        """Set the agent's mood."""
        if self.physio:
            self.physio.mood = mood


    def add_moodlet(self, moodlet: str, duration: int):
        """Add or refresh a moodlet for a given duration (in ticks)."""
        if self.physio and hasattr(self.physio, 'moodlets'):
            self.physio.moodlets[moodlet] = duration

    def update_tick(self, agent, world, tick):
        """
        Perform all per-tick physiological updates for the agent.
        """
        personality = agent.persona.get_personality() if hasattr(agent.persona, 'get_personality') else None
        traits = personality.traits if personality and hasattr(personality, 'traits') else None
        self.decay_needs(traits=traits)
        self.apply_moodlet_triggers()
        self.tick_moodlets()

    def decay_needs(self, traits=None):
        if self.physio and hasattr(self.physio, 'decay_needs'):
            self.physio.decay_needs(traits=traits)

    def apply_moodlet_triggers(self):
        if not self.physio:
            return
        # Hunger moodlet
        if getattr(self.physio, 'hunger', 0) > 0.9:
            self.physio.moodlets['starving'] = 5
        # Energy moodlet
        if getattr(self.physio, 'energy', 1) < 0.1:
            self.physio.moodlets['exhausted'] = 5
        # Social moodlet
        if getattr(self.physio, 'social', 1) < 0.1:
            self.physio.moodlets['lonely'] = 5
        # Fun moodlet
        if getattr(self.physio, 'fun', 1) < 0.1:
            self.physio.moodlets['bored'] = 5
        # Hygiene moodlet
        if getattr(self.physio, 'hygiene', 1) < 0.1:
            self.physio.moodlets['dirty'] = 5
        # Comfort moodlet
        if getattr(self.physio, 'comfort', 1) < 0.1:
            self.physio.moodlets['uncomfortable'] = 5
        # Bladder moodlet
        if getattr(self.physio, 'bladder', 1) < 0.05:
            self.physio.moodlets['desperate'] = 5
        # Stress moodlet
        if getattr(self.physio, 'stress', 0) > 0.9:
            self.physio.moodlets['overwhelmed'] = 5

    def tick_moodlets(self):
        if self.physio and hasattr(self.physio, 'moodlets'):
            expired = [k for k, v in self.physio.moodlets.items() if v <= 1]
            for k in expired:
                del self.physio.moodlets[k]
            for k in self.physio.moodlets:
                self.physio.moodlets[k] -= 1
