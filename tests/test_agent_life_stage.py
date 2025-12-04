"""
Pytest-based tests for agent life stages and aging logic.
"""
import pytest
from sim.agents.agents import Agent, Persona

@pytest.mark.parametrize("age,expected_stage", [
    (0, "infant"),
    (2, "infant"),
    (3, "toddler"),
    (5, "toddler"),
    (6, "child"),
    (12, "child"),
    (13, "teen"),
    (19, "teen"),
    (20, "young adult"),
    (35, "young adult"),
    (36, "adult"),
    (64, "adult"),
    (65, "elder"),
    (80, "elder"),
])
def test_life_stage_assignment(age, expected_stage):
    persona = Persona(name="Test", age=age, job="none", city="TestCity", bio="", values=[], goals=[])
    agent = Agent(persona=persona)
    agent.update_life_stage()
    assert agent.persona.life_stage == expected_stage


def test_life_stage_transition():
    persona = Persona(name="Test", age=2, job="none", city="TestCity", bio="", values=[], goals=[])
    agent = Agent(persona=persona)
    agent.update_life_stage()
    assert agent.persona.life_stage == "infant"
    # Age up to toddler
    agent.persona.age = 3
    agent.update_life_stage()
    assert agent.persona.life_stage == "toddler"
    # Age up to child
    agent.persona.age = 6
    agent.update_life_stage()
    assert agent.persona.life_stage == "child"
    # Age up to teen
    agent.persona.age = 13
    agent.update_life_stage()
    assert agent.persona.life_stage == "teen"
    # Age up to young adult
    agent.persona.age = 20
    agent.update_life_stage()
    assert agent.persona.life_stage == "young adult"
    # Age up to adult
    agent.persona.age = 36
    agent.update_life_stage()
    assert agent.persona.life_stage == "adult"
    # Age up to elder
    agent.persona.age = 65
    agent.update_life_stage()
    assert agent.persona.life_stage == "elder"


def test_life_stage_behavior_restrictions():
    persona = Persona(name="Test", age=1, job="none", city="TestCity", bio="", values=[], goals=[])
    agent = Agent(persona=persona)
    agent.update_life_stage()
    # Infants should not be able to work
    from sim.agents.modules.agent_plan_logic import AgentPlanLogic
    AgentPlanLogic.update_plan(agent)
    assert "WORK" not in agent.plan
    # Age up to adult
    agent.persona.age = 36
    agent.update_life_stage()
    AgentPlanLogic.update_plan(agent)
    # Adults should be able to work if conscientiousness is high
    agent.persona.traits["conscientiousness"] = 1.0
    AgentPlanLogic.update_plan(agent)
    assert "WORK" in agent.plan


def test_aging_effect_on_behavior():
    persona = Persona(name="Test", age=64, job="none", city="TestCity", bio="", values=[], goals=[])
    agent = Agent(persona=persona)
    agent.update_life_stage()
    # Adult can work
    agent.persona.traits["conscientiousness"] = 1.0
    from sim.agents.modules.agent_plan_logic import AgentPlanLogic
    AgentPlanLogic.update_plan(agent)
    assert "WORK" in agent.plan
    # Age up to elder
    agent.persona.age = 65
    agent.update_life_stage()
    AgentPlanLogic.update_plan(agent)
    # Elder should not be able to work
    assert "WORK" not in agent.plan
