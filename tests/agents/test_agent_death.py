"""
Pytest-based tests for agent death conditions and consequences.
"""
import pytest
from sim.agents.agents import Agent, Persona
from sim.agents.physio import Physio

@pytest.mark.parametrize("age,expected_alive", [
    (99, True),
    (100, False),
    (101, False),
])
def test_death_by_old_age(age, expected_alive):
    persona = Persona(name="Test", age=age, job="none", city="TestCity", bio="", values=[], goals=[])
    agent = Agent(persona=persona)
    agent.tick_update(world=None, tick=1)
    assert agent.alive == expected_alive
    if not expected_alive:
        assert agent.time_of_death == 1


def test_death_by_starvation():
    persona = Persona(name="Test", age=30, job="none", city="TestCity", bio="", values=[], goals=[])
    physio = Physio(hunger=0)
    agent = Agent(persona=persona, physio=physio)
    agent.tick_update(world=None, tick=2)
    assert not agent.alive
    assert agent.time_of_death == 2


def test_death_by_exhaustion():
    persona = Persona(name="Test", age=30, job="none", city="TestCity", bio="", values=[], goals=[])
    physio = Physio(energy=0)
    agent = Agent(persona=persona, physio=physio)
    agent.tick_update(world=None, tick=3)
    assert not agent.alive
    assert agent.time_of_death == 3


def test_death_by_stress():
    persona = Persona(name="Test", age=30, job="none", city="TestCity", bio="", values=[], goals=[])
    physio = Physio(stress=1)
    agent = Agent(persona=persona, physio=physio)
    agent.tick_update(world=None, tick=4)
    assert not agent.alive
    assert agent.time_of_death == 4


def test_death_by_bladder_failure():
    persona = Persona(name="Test", age=30, job="none", city="TestCity", bio="", values=[], goals=[])
    physio = Physio(bladder=0)
    agent = Agent(persona=persona, physio=physio)
    agent.tick_update(world=None, tick=5)
    assert not agent.alive
    assert agent.time_of_death == 5
