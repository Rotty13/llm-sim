"""
Unit tests for sim.agents.discourse_model
"""
import pytest
from sim.agents.discourse_model import Agent, DiscourseModel

def test_single_actor_conversation_probability():
    alice = Agent("Alice")
    bob = Agent("Bob")
    model = DiscourseModel([alice, bob])
    context = {"location": "lounge"}
    # No intention
    assert 0.2 <= model.single_actor_conversation_probability(alice, bob, context) <= 0.4
    # With intention
    alice.intentions = ["Bob"]
    assert model.single_actor_conversation_probability(alice, bob, context) > 0.2
    # With intention and location
    bob.name = "Jamie"
    alice.intentions = ["Jamie"]
    assert model.single_actor_conversation_probability(alice, bob, context) > 0.2

def test_multiple_actor_conversation_start_probability():
    alice = Agent("Alice")
    bob = Agent("Bob")
    jamie = Agent("Jamie")
    model = DiscourseModel([alice, bob, jamie])
    context = {"location": "lounge"}
    alice.intentions = ["Bob", "Jamie"]
    all_nearby = [bob, jamie]
    # Both
    prob_both = model.multiple_actor_conversation_start_probability(alice, all_nearby, all_nearby, context)
    assert 0.0 < prob_both <= 1.0
    # Just Bob
    prob_bob = model.multiple_actor_conversation_start_probability(alice, all_nearby, [bob], context)
    assert 0.0 < prob_bob <= 1.0
    # Just Jamie
    prob_jamie = model.multiple_actor_conversation_start_probability(alice, all_nearby, [jamie], context)
    assert 0.0 < prob_jamie <= 1.0
    # Empty group
    assert model.multiple_actor_conversation_start_probability(alice, all_nearby, [], context) == 0.0

def test_should_conclude():
    alice = Agent("Alice")
    model = DiscourseModel([alice])
    assert model.should_conclude(["Goodbye!"])
    assert model.should_conclude(["That's all for now."])
    assert not model.should_conclude(["Let's continue talking."])
