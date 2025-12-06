"""
Test social influence integration in agent planning.
"""
import pytest
from sim.agents.agents import Agent, Persona
from sim.agents.modules.agent_social import AgentSocial
from sim.agents.modules.agent_plan_logic import AgentPlanLogic

@pytest.fixture
def agent():
    persona = Persona(
        name="InfluencedAgent",
        age=28,
        job="tester",
        city="SimCity",
        bio="Bio",
        values=["friendship"],
        goals=["connect"],
        traits={"extraversion": 0.7},
        aspirations=["socialize"],
        emotional_modifiers={},
        age_transitions={},
        life_stage="adult"
    )
    ag = Agent(persona=persona, place="Cafe")
    ag.social = AgentSocial()
    return ag

def test_social_influence_modifier_boosts_say(agent):
    # Simulate recent topic and influential connection
    agent.social.topic_history.append(("Alice", "social_life"))
    agent.social.connections["Alice"] = {"influence": 1.0}
    # Set social need low to trigger SAY condition (social < 0.5)
    agent.physio.social = 0.4
    # Should boost extraversion score above threshold
    AgentPlanLogic.update_plan(agent)
    assert "SAY" in agent.plan

def test_social_influence_no_boost(agent):
    # No recent topic or influential connection
    agent.social.topic_history.clear()
    agent.social.connections.clear()
    # Extraversion below threshold, no boost
    agent.persona.traits["extraversion"] = 0.7
    AgentPlanLogic.update_plan(agent)
    assert "SAY" not in agent.plan
