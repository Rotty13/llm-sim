"""
persona.py

Defines the Persona dataclass for agent identity, personality, and life characteristics in llm-sim.

Key Class:
- Persona: Represents an agent's identity, job, values, goals, and personality traits.

LLM Usage:
- None directly; used by Agent and simulation modules.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from sim.agents.personality import Personality

@dataclass
class Persona:
    """Represents an agent's identity, personality, and life characteristics."""
    name: str
    age: int
    job: str
    city: str
    bio: str
    values: List[str]
    goals: List[str]
    traits: Dict[str, float] = field(default_factory=dict)
    aspirations: List[str] = field(default_factory=list)
    emotional_modifiers: Dict[str, float] = field(default_factory=dict)
    age_transitions: Dict[str, int] = field(default_factory=dict)
    life_stage: str = "adult"
    personality: Optional[Personality] = None

    def get_personality(self) -> Personality:
        if self.personality is None:
            self.personality = Personality(traits=self.traits, aspirations={asp: 0.5 for asp in self.aspirations})
        return self.personality
