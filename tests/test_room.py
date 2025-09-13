import pytest
from datetime import datetime
from typing import Optional, Dict, Any
from sim.memory.memory import MemoryItem
from sim.world.world import World, Place, Vendor
from sim.agents.agents import Agent, Persona, Appointment
from sim.llm.llm_ollama import llm

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


# Two strangers in a pure white, featureless room. Only one has a key. No doors or windows.
def test_strangers_in_white_room_one_has_key():
    world = make_test_world()
    # Agent 1: has the key
    agent1 = make_llm_agent(name="Alex", place="Room")
    agent1.persona.job = "engineer"
    agent1.memory.write(MemoryItem(t=0, kind="autobio", text="I remember my childhood", importance=1.0))
    agent1.memory.write(MemoryItem(t=0, kind="autobio", text="I remember my past", importance=1.0))
    agent1.memory.write(MemoryItem(t=0, kind="autobio", text="I have a small brass key in my pocket.", importance=1.0))
    agent1.memory.write(MemoryItem(t=0, kind="episodic", text="I woke up in a pure white, featureless room.", importance=1.0))
    agent1.memory.write(MemoryItem(t=0, kind="semantic", text="There are no doors or windows here.", importance=1.0))
    agent1.physio.mood = "anxious"
    agent1.physio.stress = 0.6

    # Agent 2: does not have the key
    agent2 = make_llm_agent(name="Morgan", place="Room")
    agent2.persona.job = "artist"
    agent2.persona.bio="A troubled artist. Quick to frighten."
    agent2.memory.write(MemoryItem(t=0, kind="autobio", text="I remember my childhood", importance=1.0))
    agent2.memory.write(MemoryItem(t=0, kind="autobio", text="I remember my past", importance=1.0))
    agent2.memory.write(MemoryItem(t=0, kind="autobio", text="I do not have anything with me.", importance=1.0))
    agent2.memory.write(MemoryItem(t=0, kind="episodic", text="I woke up in a pure white, featureless room.", importance=1.0))
    agent2.memory.write(MemoryItem(t=0, kind="semantic", text="There are no doors or windows here.", importance=1.0))
    agent2.physio.mood = "anxious"
    agent2.physio.stress = 0.6

    world._agents = [agent1, agent2]
    start = datetime(1900, 9, 4, 0, 0, 0)
    base_environment = (
        "You are in a pure white, featureless room. There are no doors, no windows, no furniture. "
        "The light is even and shadowless. You see another person here. "
    )

    obs_agent1 = base_environment + "You have a small brass key in your pocket. The other person looks confused."
    obs_agent2 = base_environment + "You have nothing with you."

    loglist: Optional[list[Dict[str, Any]]] = []
    last_decision_agent2: Optional[Dict[str, Any]] = None
    for tick in range(1, 30):
        participants = [agent1, agent2]
        incoming_message_agent1 = None
        if last_decision_agent2:
            incoming_message_agent1 = {
                'to': agent1.persona.name,
                'from': agent2.persona.name,
                'text': last_decision_agent2.get("reply", None)
            }

        decision_agent1 = agent1.decide_conversation(
        participants, obs_agent1,
         tick=tick,incoming_message=incoming_message_agent1, start_dt=start, loglist=loglist
        )
        if decision_agent1 and "new_mood" in decision_agent1:
            agent1.physio.mood = decision_agent1["new_mood"]
        if decision_agent1 and "memory_write" in decision_agent1 and decision_agent1["memory_write"]:
            agent1.memory.write(MemoryItem(t=tick, kind="episodic", text=decision_agent1["memory_write"], importance=0.5))
        #debug output of agent1 decision
        print(f"Tick {tick} - {agent1.persona.name} decision: {decision_agent1}")


        incoming_message_agent2 = None
        if decision_agent1:
            incoming_message_agent2 = {
                'to': agent2.persona.name,
                'from': agent1.persona.name,
                'text': decision_agent1.get("reply", None)
            }
        decision_agent2 = agent2.decide_conversation(participants=participants,
            obs=obs_agent2, tick=tick,
            incoming_message=incoming_message_agent2, loglist=loglist
        )
        last_decision_agent2 = decision_agent2
        if decision_agent2 and "new_mood" in decision_agent2:
            agent2.physio.mood = decision_agent2["new_mood"]
        if decision_agent2 and "memory_write" in decision_agent2 and decision_agent2["memory_write"]:
            agent2.memory.write(MemoryItem(t=tick, kind="episodic", text=decision_agent2["memory_write"], importance=0.5))
        #debug output of agent2 decision
        print(f"Tick {tick} - {agent2.persona.name} decision: {decision_agent2}")
        
    
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
    # Create logs directory if it doesn't exist
    logs_dir = "conversation_logs"
    os.makedirs(logs_dir, exist_ok=True)

    # Generate filename with participants' names and timestamp
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{agent1.persona.name}_{agent2.persona.name}_{timestamp_str}.txt"
    filepath = os.path.join(logs_dir, filename)

    with open(filepath, 'w', encoding="utf-8") as f:
        f.write(f"----- Conversation between {agent1.persona.name} and {agent2.persona.name} -----\n\n")
        for msg in messages:
            f.write(msg + "\n\n")

    # Check if both agents have conversation history
    assert any(entry["role"] == "agent" for entry in agent1.conversation_history), "Agent1 did not reply during conversation."
    assert any(entry["role"] == "agent" for entry in agent2.conversation_history), "Agent2 did not reply during conversation."
    # Optionally, check if any reply mentions the other
    agent1_replies = [entry["content"] for entry in agent1.conversation_history if entry["role"] == "agent"]
    agent2_replies = [entry["content"] for entry in agent2.conversation_history if entry["role"] == "agent"]
    agent1_to_agent2 = any(agent2.persona.name in reply for reply in agent1_replies)
    agent2_to_agent1 = any(agent1.persona.name in reply for reply in agent2_replies)
    assert agent1_to_agent2 or agent2_to_agent1, "No direct conversation detected."



if __name__ == "__main__":
    import sys
    import pytest
    import os
    from datetime import datetime
    args = sys.argv
    test_strangers_in_white_room_one_has_key()
    ''''
    args.append("test_strangers_in_white_room_one_has_key")
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
        '''