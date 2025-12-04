"""
Unit tests for expanded mood/emotion system and moodlet-driven behaviors.
"""
import pytest
from sim.agents.agents import Agent, Physio, Persona

class DummyWorld:
    pass

def make_agent_with_physio(physio):
    persona = Persona(
        name="TestAgent",
        age=30,
        job="tester",
        city="TestCity",
        bio="bio",
        values=[],
        goals=[],
        traits={},
        aspirations=[],
        emotional_modifiers={},
        age_transitions={},
        life_stage="adult"
    )
    return Agent(persona=persona, place="TestPlace", physio=physio)

def test_starving_moodlet_triggers_eat():
    physio = Physio(hunger=0.95)
    agent = make_agent_with_physio(physio)
    agent.plan = []
    agent.tick_update(DummyWorld(), tick=1)
    assert "starving" in agent.physio.moodlets
    assert "EAT" in agent.plan

def test_exhausted_moodlet_triggers_rest():
    physio = Physio(energy=0.05)
    agent = make_agent_with_physio(physio)
    agent.plan = []
    agent.tick_update(DummyWorld(), tick=1)
    assert "exhausted" in agent.physio.moodlets
    assert "REST" in agent.plan

def test_angry_emotional_state_triggers_say():
    physio = Physio()
    agent = make_agent_with_physio(physio)
    agent.plan = []
    agent.set_emotional_state("angry")
    agent.tick_update(DummyWorld(), tick=1)
    assert "SAY" in agent.plan

def test_happy_emotional_state_triggers_explore():
    physio = Physio()
    agent = make_agent_with_physio(physio)
    agent.plan = []
    agent.set_emotional_state("happy")
    agent.tick_update(DummyWorld(), tick=1)
    assert "EXPLORE" in agent.plan
