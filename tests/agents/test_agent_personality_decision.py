"""
Tests that agent decisions are influenced by personality traits and aspirations.
"""
import pytest
from sim.agents.agents import Persona, Agent, Physio
from sim.agents.personality import Personality

class DummyWorld:
    pass

def make_agent(traits, aspirations, physio=None):
    persona = Persona(
        name="TestAgent",
        age=30,
        job="developer",
        city="TestCity",
        bio="Test bio",
        values=[],
        goals=[],
        traits=traits,
        aspirations=aspirations,
        emotional_modifiers={},
        age_transitions={},
        life_stage="adult"
    )
    physio = physio or Physio()
    agent = Agent(persona=persona, physio=physio, place="TestPlace")
    agent.plan = []
    return agent

def test_high_conscientiousness_prefers_work():
    agent = make_agent({"conscientiousness": 0.9}, ["wealth"])
    if agent.physio is not None:
        agent.physio.energy = 0.8
    agent.tick_update(DummyWorld(), tick=1)
    assert "WORK" in agent.plan

def test_high_extraversion_prefers_social():
    agent = make_agent({"extraversion": 0.95}, ["friendship"])
    if agent.physio is not None:
        agent.physio.social = 0.2
    agent.tick_update(DummyWorld(), tick=1)
    assert "SAY" in agent.plan

def test_high_openness_prefers_explore():
    agent = make_agent({"openness": 0.95}, ["exploration"])
    if agent.physio is not None:
        agent.physio.energy = 0.5
    agent.tick_update(DummyWorld(), tick=1)
    assert "EXPLORE" in agent.plan

def test_low_trait_no_action():
    agent = make_agent({"conscientiousness": 0.1, "extraversion": 0.1, "openness": 0.1}, ["wealth", "friendship", "exploration"])
    if agent.physio is not None:
        agent.physio.energy = 0.8
        agent.physio.social = 0.8
    agent.tick_update(DummyWorld(), tick=1)
    # Should not add any plan actions due to low trait/aspiration effect
    assert agent.plan == []
