"""
Unit tests for expanded needs system and need-driven behaviors.
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

def test_hunger_triggers_eat():
    physio = Physio(hunger=0.9)
    agent = make_agent_with_physio(physio)
    agent.plan = []
    agent.tick_update(DummyWorld(), tick=1)
    assert "EAT" in agent.plan

def test_low_energy_triggers_rest():
    physio = Physio(energy=0.1)
    agent = make_agent_with_physio(physio)
    agent.plan = []
    agent.tick_update(DummyWorld(), tick=1)
    assert "REST" in agent.plan

def test_high_stress_triggers_relax():
    physio = Physio(stress=0.8)
    agent = make_agent_with_physio(physio)
    agent.plan = []
    agent.tick_update(DummyWorld(), tick=1)
    assert "RELAX" in agent.plan

def test_low_social_triggers_say():
    physio = Physio(social=0.2)
    agent = make_agent_with_physio(physio)
    agent.plan = []
    agent.tick_update(DummyWorld(), tick=1)
    assert "SAY" in agent.plan

def test_low_fun_triggers_explore():
    physio = Physio(fun=0.2)
    agent = make_agent_with_physio(physio)
    agent.plan = []
    agent.tick_update(DummyWorld(), tick=1)
    assert "EXPLORE" in agent.plan

def test_low_hygiene_triggers_clean():
    physio = Physio(hygiene=0.2)
    agent = make_agent_with_physio(physio)
    agent.plan = []
    agent.tick_update(DummyWorld(), tick=1)
    assert "CLEAN" in agent.plan

def test_low_comfort_triggers_relax():
    physio = Physio(comfort=0.2)
    agent = make_agent_with_physio(physio)
    agent.plan = []
    agent.tick_update(DummyWorld(), tick=1)
    assert "RELAX" in agent.plan

def test_low_bladder_triggers_toilet():
    physio = Physio(bladder=0.1)
    agent = make_agent_with_physio(physio)
    agent.plan = []
    agent.tick_update(DummyWorld(), tick=1)
    assert "TOILET" in agent.plan
