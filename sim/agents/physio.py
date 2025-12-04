"""
physio.py

Defines the Physio dataclass for agent physiological and emotional state in llm-sim.

Key Class:
- Physio: Represents an agent's physiological state (hunger, energy, stress, mood, etc.).

LLM Usage:
- None directly; used by Agent and simulation modules.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class Physio:
    """Represents an agent's physiological and emotional state."""
    hunger: float = 0.3
    energy: float = 0.8
    stress: float = 0.2
    mood: str = "neutral"
    social: float = 0.5
    fun: float = 0.5
    moodlets: Dict[str, int] = field(default_factory=dict)
    emotional_state: str = "neutral"
    hygiene: float = 0.8
    comfort: float = 0.8
    bladder: float = 0.8

    def decay_needs(self, traits: Optional[Dict[str, float]] = None):
        """
        Decay physiological needs over time, modulated by personality traits.
        Higher neuroticism increases stress accumulation; conscientiousness slows hunger decay.
        """
        traits = traits or {}
        # Base decay rates
        hunger_decay = 0.02
        energy_decay = 0.01
        stress_decay = 0.01
        hygiene_decay = 0.01
        comfort_decay = 0.01
        bladder_decay = 0.02

        # Trait modulation
        hunger_decay *= (1.0 - 0.3 * traits.get("conscientiousness", 0.5))
        stress_decay *= (1.0 + 0.4 * traits.get("neuroticism", 0.5))
        energy_decay *= (1.0 - 0.2 * traits.get("extraversion", 0.5))

        # Apply decay
        self.hunger = min(1.0, self.hunger + hunger_decay)
        self.energy = max(0.0, self.energy - energy_decay)
        self.stress = min(1.0, self.stress + stress_decay)
        self.social = max(0.0, self.social - 0.01)
        self.fun = max(0.0, self.fun - 0.01)
        self.hygiene = max(0.0, self.hygiene - hygiene_decay)
        self.comfort = max(0.0, self.comfort - comfort_decay)
        self.bladder = max(0.0, self.bladder - bladder_decay)
