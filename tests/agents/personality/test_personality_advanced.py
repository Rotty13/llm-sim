"""
Advanced tests for Personality class: context sensitivity, edge cases, and integration with Persona.
"""
import pytest
from sim.agents.personality import Personality
from sim.agents.agents import Persona

def test_trait_effect_context():
    p = Personality(traits={"openness": 0.9})
    context = {"situation": "novelty"}
    # Context not used yet, but test for future extension
    assert p.trait_effect("openness", context) == 0.8

def test_aspiration_effect_edge():
    p = Personality(aspirations={"achievement": 1.2, "ambition": -0.2})
    # Should clamp or handle out-of-range gracefully
    assert p.aspiration_effect("achievement") == 1.4
    assert p.aspiration_effect("ambition") == -1.4

def test_emotion_modifier_extremes():
    p = Personality()
    assert p.emotion_modifier("anger", 2.0) == -2.0
    assert p.emotion_modifier("trust", 0.0) == 0.0

def test_persona_integration():
    persona = Persona(
        name="TestAgent",
        age=30,
        job="developer",
        city="TestCity",
        bio="Test bio",
        values=["curiosity"],
        goals=["explore"],
        traits={"openness": 0.8, "conscientiousness": 0.6, "extraversion": 0.4, "agreeableness": 0.7, "neuroticism": 0.3},
        aspirations=["achievement", "friendship"],
        emotional_modifiers={"baseline_mood": 0.2, "emotional_reactivity": 0.6},
        age_transitions={},
        life_stage="adult"
    )
    personality = persona.get_personality()
    assert isinstance(personality, Personality)
    assert personality.traits["openness"] == 0.8
    assert "achievement" in personality.aspirations

def test_summary_immutability():
    p = Personality(traits={"openness": 0.7})
    summary = p.summary()
    summary["openness"] = 0.0
    # Should not affect original traits
    assert p.traits["openness"] == 0.7
