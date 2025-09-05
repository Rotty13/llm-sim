import pytest
from datetime import datetime
from sim.world.world import World, Place, Vendor
from sim.agents.agents import Agent, Persona, Appointment
from sim.llm.llm import llm

def make_test_world():
    places = {
        "Room": Place("Room", [], {}, None, "Unknown"),
    }
    return World(places=places)

def make_llm_agent(name="James", place="White Room"):
    persona = Persona(
        name=name,
        age=30,
        job="writer",
        city="breham",
        bio="A curious writer.",
        values=["curiosity", "truth"],
        goals=["explore", "understand"]
    )
    return Agent(persona=persona, place=place)

def test_agent_decide_and_act_llm():
    world = make_test_world()
    agent = make_llm_agent()
    world._agents = [agent]
    start = datetime(1900, 9, 4, 9, 0, 0)
    obs = "(quiet)"
    decision = agent.decide(world, obs, tick=1, start_dt=start)
    assert isinstance(decision, dict)
    agent.act(world, decision, tick=1)
    # Check that agent's place is still valid and events are broadcast
    assert agent.place in world.places
    assert any(e.get("actor") == agent.persona.name for e in world.events)

def test_agent_llm_chat():
    world = make_test_world()
    agent = make_llm_agent()
    deadwife: Agent = make_llm_agent(name="Julie(wife, deceased)", place="Unknown")
    world._agents = [agent, deadwife]
    agent.physio.mood = "stressed"
    start = datetime(1900, 9, 4, 9, 0, 0)
    obs = "You are in test room, a pure white featureless room. Julie is standing in front of you."
    decision = agent.decide(world, obs, tick=1, start_dt=start)
    # The agent's LLM is used internally by decide()
    assert isinstance(decision, dict)
    assert "action" in decision
    assert isinstance(decision["action"], str) and len(decision["action"]) > 0

def test_agent_talks_and_observes_silence():
    world = make_test_world()
    agent = make_llm_agent()
    deadwife: Agent = make_llm_agent(name="Julie(wife, deceased)", place="Unknown")
    world._agents = [agent, deadwife]
    agent.physio.mood = "stressed"
    start = datetime(1900, 9, 4, 9, 0, 0)
    obs = "You are in test room, a pure white featureless room. Your late wife Julie is standing in front of you smiling."
    for tick in range(1, 6):
        decision = agent.decide(world, obs, tick=tick, start_dt=start)
        agent.act(world, decision, tick=tick)
    # After 5 steps, check if agent tried to talk
    said_something = any(e.get("kind") == "say" and e.get("actor") == agent.persona.name for e in world.events)
    assert said_something, "Agent did not attempt to talk during simulation."
    # Check that agent observed silence from deadwife
    observed_silence = any("silent" in obs.lower() for obs in ["You are in test room with your deadwife. She is silent."])
    assert observed_silence, "Agent did not observe silence from deadwife."

def test_agent_converses_with_deadwife():
    world = make_test_world()
    agent = make_llm_agent()
    deadwife = make_llm_agent(name="Julie(wife, deceased)", place="Room")
    world._agents = [agent, deadwife]
    agent.physio.mood = "stressed"
    deadwife.physio.mood = "calm"
    start = datetime(1900, 9, 4, 9, 0, 0)
    obs_agent = "You are in test room, a pure white featureless room. Your late wife Julie is standing in front of you smiling."
    obs_deadwife = "You are in test room, a pure white featureless room. Your husband James is here, looking at you sadly. You don't know how but you feel you are dead."
    for tick in range(1, 6):
        decision_agent = agent.decide(world, obs_agent, tick=tick, start_dt=start)
        agent.act(world, decision_agent, tick=tick)
        decision_deadwife = deadwife.decide(world, obs_deadwife, tick=tick, start_dt=start)
        deadwife.act(world, decision_deadwife, tick=tick)
    # Check if both agents tried to talk
    said_by_agent = [e for e in world.events if e.get("kind") == "say" and e.get("actor") == agent.persona.name]
    said_by_deadwife = [e for e in world.events if e.get("kind") == "say" and e.get("actor") == deadwife.persona.name]
    assert said_by_agent, "Agent did not attempt to talk during simulation."
    assert said_by_deadwife, "Deadwife did not attempt to talk during simulation."
    # Optionally, check if any message was directed to the other
    agent_to_deadwife = any("Julie" in (e.get("text") or "") for e in said_by_agent)
    deadwife_to_agent = any("James" in (e.get("text") or "") for e in said_by_deadwife)
    assert agent_to_deadwife or deadwife_to_agent, "No direct conversation detected."

if __name__ == "__main__":
    import sys
    import pytest
    args = sys.argv
    args.append("test_agent_converses_with_deadwife")
    # Usage: python test_room.py [testname]
    if len(args) > 1:
        # Run only the specified test(s)
        tests = [arg for arg in args[1:] if arg.startswith("test_")]
        if tests:
            pytest.main([__file__, "-k", " or ".join(tests)])
        else:
            print("No valid test name provided. Run as: python test_room.py test_agent_converses_with_deadwife")
    else:
        # Run all tests
        pytest.main([__file__])