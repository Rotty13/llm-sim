"""
test_agent_relationships.py

Tests for AgentRelationships relationship types and decision effect logic.
"""
import pytest
from sim.agents.modules.agent_relationships import AgentRelationships

def test_set_and_get_relationship_type():
    rel = AgentRelationships()
    rel.set_relationship("Bob", rel_type="friend")
    assert rel.get_relationship_type("Bob") == "friend"
    rel.set_relationship_type("Bob", "rival")
    assert rel.get_relationship_type("Bob") == "rival"

def test_relationship_effect_on_decision_friend():
    rel = AgentRelationships()
    rel.set_relationship("Alice", affinity=0.6, trust=0.7, rel_type="friend")
    effect = rel.relationship_effect_on_decision("Alice")
    assert effect > 1.0  # affinity + trust for friend

def test_relationship_effect_on_decision_family():
    rel = AgentRelationships()
    rel.set_relationship("Carol", affinity=0.5, trust=0.5, rel_type="family")
    effect = rel.relationship_effect_on_decision("Carol")
    assert effect > 1.0  # affinity + trust + 0.2 for family

def test_relationship_effect_on_decision_rival():
    rel = AgentRelationships()
    rel.set_relationship("Dave", rivalry=0.8, rel_type="rival")
    effect = rel.relationship_effect_on_decision("Dave")
    assert effect < 0.0  # negative effect for rival

def test_relationship_effect_on_decision_default():
    rel = AgentRelationships()
    rel.set_relationship("Eve", affinity=0.3, trust=0.2)
    effect = rel.relationship_effect_on_decision("Eve")
    assert effect >= 0.0
