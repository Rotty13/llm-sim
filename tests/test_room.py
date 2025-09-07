import pytest
from datetime import datetime
from typing import Optional, Dict, Any
from sim.memory.memory import MemoryItem
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
        goals=["understand what is happening"]
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
    obs = "You are in James' room. Julie is standing in front of you."
    decision = agent.decide(world, obs, tick=1, start_dt=start)
    # The agent's LLM is used internally by decide()
    assert isinstance(decision, dict)
    assert "action" in decision
    assert isinstance(decision["action"], str) and len(decision["action"]) > 0


def test_agent_converses_with_deadwife():
    world = make_test_world()
    agent = make_llm_agent()
    deadwife = make_llm_agent(name="Julie", place="Room")
    world._agents = [agent, deadwife]
    start = datetime(1900, 9, 4, 0, 0, 0)
    base_environment = (
        "You are in the kitchen of James' house. "
        "The room is dimly lit by a single flickering candle on the old wooden table. "
        "Shadows dance across the cracked tiles and faded wallpaper, "
        "and the air carries a faint chill, "
        "Cobwebs hang in the corners, and the silence is broken only by the distant ticking of a grandfather clock. "
    )

    #main agent
    agent.physio.mood = "stressed"
    agent.physio.stress = 0.6
    agent.memory.write(MemoryItem(t=0, kind="autobio", text="My wife Julie died 5 years ago(1895) in a carriage accident.", importance=1.0))
    agent.memory.write(MemoryItem(t=0, kind="autobio", text="I miss my wife Julie dearly.", importance=1.0))
    agent.memory.write(MemoryItem(t=0, kind="autobio", text="I remember everything up and including the current date", importance=1.0))
    agent.memory.write(MemoryItem(t=0, kind="episodic", text="I've just woken up", importance=.5))
    agent.memory.write(MemoryItem(t=0, kind="episodic", text="I woke up to get something to drink", importance=0.3))
    obs_agent = base_environment + "Your late wife Julie is standing in front of you. you want to talk to her."


    #deadwife agent
    deadwife.physio.mood = "confused"
    deadwife.physio.stress = 0.7
    deadwife.persona.job = "seamstress"
    deadwife.memory.write(MemoryItem(t=0, kind="autobio", text="james is my husband", importance=1.0))
    deadwife.memory.write(MemoryItem(t=0, kind="autobio", text="I'm a seamstress", importance=1.0))
    deadwife.memory.write(MemoryItem(t=0, kind="autobio", text="I remember everything prior to 1895.", importance=1.0))
    deadwife.memory.write(MemoryItem(t=0, kind="semantic", text="it is the year of 1895.", importance=1.0))
    deadwife.memory.write(MemoryItem(t=0, kind="episodic", text="I was taking a carriage ride.", importance=1.0))
    obs_deadwife = base_environment + "Your husband James is here. You don't know how but you feel you are dead."


    loglist: Optional[list[Dict[str, Any]]] = []
    last_decision_deadwife: Optional[Dict[str, Any]] = None
    for tick in range(1, 10):
        # Use decide_conversation for both agents
        participants = [agent, deadwife]
        incoming_message_agent = None
        if last_decision_deadwife:
            incoming_message_agent = {
                'to': agent.persona.name,
                'from': deadwife.persona.name,
                'text': last_decision_deadwife.get("reply", None)
            }
        decision_agent = agent.decide_conversation(
            world, obs_agent, participants=participants,
            incoming_message=incoming_message_agent, tick=tick, start_dt=start,loglist=loglist
        )
        if decision_agent and "new_mood" in decision_agent:
            agent.physio.mood = decision_agent["new_mood"]
        if decision_agent and "memory_write" in decision_agent and decision_agent["memory_write"]:
            agent.memory.write(MemoryItem(t=tick, kind="episodic", text=decision_agent["memory_write"], importance=0.5))

        incoming_message_deadwife = None
        if decision_agent:
            incoming_message_deadwife = {
                'to': deadwife.persona.name,
                'from': agent.persona.name,
                'text': decision_agent.get("reply", None)
            }
        decision_deadwife = deadwife.decide_conversation(
            world, obs_deadwife, participants=participants,
            incoming_message=incoming_message_deadwife, tick=tick,loglist=loglist
        )
        last_decision_deadwife = decision_deadwife
        if decision_deadwife and "new_mood" in decision_deadwife:
            deadwife.physio.mood = decision_deadwife["new_mood"]
        if decision_deadwife and "memory_write" in decision_deadwife and decision_deadwife["memory_write"]:
            deadwife.memory.write(MemoryItem(t=tick, kind="episodic", text=decision_deadwife["memory_write"], importance=0.5))
        pass


        
    
    # Combine conversation histories and output to a file
    import json
    def extract_message(entry):
        # Try to parse content as JSON to extract 'from' and 'to'
        content = entry#json.loads(entry["content"])
        msg_from = content.get("from", None)
        msg_to = content.get("to", None)
        msg_text = content.get("reply", content.get("text", entry))
        content_private_thought = content.get("private_thought", "")
        content_memory_write = content.get("memory_write", "")
        return f"""
from: {msg_from}, to: {msg_to}
private_thought: '{content_private_thought}'
memory_write: '{content_memory_write}'
text: '{msg_text}'
""".strip()


    messages = [extract_message(entry) for entry in loglist]
    with open("conversation_decisions_output.txt",'w', encoding="utf-8") as f:
        f.write("----- Conversation between James and Julie -----\n\n")
        for msg in messages:
            f.write(msg + "\n\n") 

    # Check if both agents have conversation history
    assert any(entry["role"] == "agent" for entry in agent.conversation_history), "Agent did not reply during conversation."
    assert any(entry["role"] == "agent" for entry in deadwife.conversation_history), "Deadwife did not reply during conversation."
    # Optionally, check if any reply mentions the other
    agent_replies = [entry["content"] for entry in agent.conversation_history if entry["role"] == "agent"]
    deadwife_replies = [entry["content"] for entry in deadwife.conversation_history if entry["role"] == "agent"]
    agent_to_deadwife = any("Julie" in reply for reply in agent_replies)
    deadwife_to_agent = any("James" in reply for reply in deadwife_replies)
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