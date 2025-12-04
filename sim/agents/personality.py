"""
Personality Modeling Module

Purpose:
Defines agent personality traits, aspirations, and emotional modifiers for simulation.
Implements the Big Five model and provides trait effect logic for agent decision-making.

Key Classes:
- Personality: Stores trait values and calculates effects.

LLM Usage: None (no fallback allowed)

CLI Arguments: None
"""

from typing import Dict, Any, Optional

class Personality:
    """
    Represents an agent's personality using the Big Five traits and aspirations.
    Provides methods to calculate trait effects on agent behavior.
    """
    BIG_FIVE_TRAITS = [
        "openness",
        "conscientiousness",
        "extraversion",
        "agreeableness",
        "neuroticism"
    ]

    def __init__(self, traits: Optional[Dict[str, float]] = None, aspirations: Optional[Dict[str, Any]] = None):
        self.traits = traits or {trait: 0.5 for trait in self.BIG_FIVE_TRAITS}  # Default neutral
        self.aspirations = aspirations or {}

    def trait_effect(self, trait: str, context: Optional[Dict[str, Any]] = None) -> float:
        """
        Returns the effect modifier for a given trait in a specific context.
        """
        value = self.traits.get(trait, 0.5)
        # Basic effect: scale from -1 (low) to +1 (high)
        return (value - 0.5) * 2

    def aspiration_effect(self, aspiration: str, context: Optional[Dict[str, Any]] = None) -> float:
        """
        Returns the effect modifier for a given aspiration in a specific context.
        Example: ambition, achievement, social status, etc.
        """
        value = self.aspirations.get(aspiration, 0.5)
        return (value - 0.5) * 2

    def emotion_modifier(self, emotion: str, intensity: float = 0.5) -> float:
        """
        Returns a modifier based on current emotional state.
        Example: happiness, anger, fear, etc.
        """
        # Simple model: positive emotions boost, negative reduce
        emotion_map = {
            "happiness": 1.0,
            "anger": -1.0,
            "fear": -0.7,
            "sadness": -0.8,
            "surprise": 0.3,
            "trust": 0.7,
            "disgust": -0.9
        }
        base = emotion_map.get(emotion, 0.0)
        return base * intensity

    def summary(self) -> Dict[str, float]:
        """
        Returns a summary of trait values.
        """
        return self.traits.copy()

    # TODO: Add aspiration/emotion logic and advanced trait effects
