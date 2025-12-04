"""
Unit tests for Personality class in sim/agents/personality.py

Tests trait effect, aspiration effect, emotion modifier, initialization, and summary.
"""
import pytest
from sim.agents.personality import Personality

def test_trait_effect_basic():
    p = Personality(traits={"openness": 1.0})
    assert p.trait_effect("openness") == 1.0
    assert p.trait_effect("conscientiousness") == 0.0  # default neutral
    p = Personality(traits={"openness": 0.0})
    assert p.trait_effect("openness") == -1.0

def test_aspiration_effect_basic():
    p = Personality(aspirations={"achievement": 1.0})
    assert p.aspiration_effect("achievement") == 1.0
    assert p.aspiration_effect("ambition") == 0.0  # default neutral
    p = Personality(aspirations={"achievement": 0.0})
    assert p.aspiration_effect("achievement") == -1.0

def test_emotion_modifier():
    p = Personality()
    assert p.emotion_modifier("happiness", 1.0) == 1.0
    assert p.emotion_modifier("anger", 0.5) == -0.5
    assert p.emotion_modifier("fear", 1.0) == -0.7
    assert p.emotion_modifier("unknown", 1.0) == 0.0

def test_initialization_defaults():
    p = Personality()
    for trait in Personality.BIG_FIVE_TRAITS:
        assert trait in p.traits
        assert p.traits[trait] == 0.5
    assert p.aspirations == {}

def test_summary():
    traits = {"openness": 0.8, "conscientiousness": 0.2, "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5}
    p = Personality(traits=traits)
    assert p.summary() == traits
