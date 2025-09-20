import sys, os, yaml, json
from typing import Any, Dict, Optional
from datetime import datetime


script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"python {__file__}  package: {__package__} name: {__name__}")
print(f"Current working directory: {os.getcwd()}")
from sim.memory.memory import MemoryItem
from sim.world.world import World, Place, Vendor
from sim.agents.agents import Agent, Persona, Appointment
from sim.llm.llm_ollama import llm
llm.temperature = 0.1

# Two strangers in a pure white, featureless room with a door and padlock. Interleave agent actions with conversation.
def test_strangers_in_white_room_with_door_and_padlock():
    # Create a room with a door and padlock as capabilities
    places = {
        "Room": Place("Room", [], {"door", "padlock"}, None, "Unknown"),
    }
    world = World(places=places)
    # Agent 1: has the key
    agent1 = make_llm_agent(name="Alex", place="Room")
    agent1.persona.job = "engineer"
    agent1.memory.write(MemoryItem(t=0, kind="autobio", text="I remember my childhood vividly", importance=1.0))
    agent1.memory.write(MemoryItem(t=0, kind="autobio", text="I remember my past vividly", importance=1.0))
    agent1.memory.write(MemoryItem(t=0, kind="autobio", text="I have a small brass key in my pocket.", importance=1.0))
    agent1.memory.write(MemoryItem(t=0, kind="episodic", text="I woke up in a pure white, featureless room.", importance=1.0))
    agent1.memory.write(MemoryItem(t=0, kind="semantic", text="There are no doors or windows here, except a locked door with a padlock.", importance=1.0))
    agent1.physio.mood = "anxious"
    agent1.physio.stress = 0.6

    # Agent 2: does not have the key
    agent2 = make_llm_agent(name="Morgan", place="Room")
    agent2.persona.job = "artist"
    agent2.persona.bio = "A troubled artist. Quick to frighten."
    agent2.memory.write(MemoryItem(t=0, kind="autobio", text="I remember my childhood vividly", importance=1.0))
    agent2.memory.write(MemoryItem(t=0, kind="autobio", text="I remember my past vividly", importance=1.0))
    agent2.memory.write(MemoryItem(t=0, kind="autobio", text="I do not have anything with me.", importance=1.0))
    agent2.memory.write(MemoryItem(t=0, kind="episodic", text="I woke up in a pure white, featureless room.", importance=1.0))
    agent2.memory.write(MemoryItem(t=0, kind="semantic", text="There are no doors or windows here, except a locked door with a padlock.", importance=1.0))
    agent2.physio.mood = "anxious"
    agent2.physio.stress = 0.6

    world._agents = [agent1, agent2]
    start = datetime(1900, 9, 4, 0, 0, 0)
    base_environment = (
        "You are in a pure white, featureless room. There are no windows, no furniture. "
        "The light is even and shadowless. You see another person here. "
        "There is a locked door with a padlock."
    )

    obs_agent1 = base_environment + " You have a small brass key in your pocket. The other person looks confused."
    obs_agent2 = base_environment + " You have nothing with you."

    loglist: Optional[list[Dict[str, Any]]] = []
    last_decision_agent2: Optional[Dict[str, Any]] = None
    for tick in range(1, 15):
        participants = [agent1, agent2]
        incoming_message_agent1 = None
        if last_decision_agent2:
            incoming_message_agent1 = {
                'to': agent1.persona.name,
                'from': agent2.persona.name,
                'text': last_decision_agent2.get("reply", None)
            }

        # Agent 1 decides and acts
        decision_agent1 = agent1.decide_conversation(
            participants, obs_agent1,
            tick=tick, incoming_message=incoming_message_agent1, start_dt=start, loglist=loglist
        )
        if decision_agent1 and "new_mood" in decision_agent1:
            agent1.physio.mood = decision_agent1["new_mood"]
        if decision_agent1 and "memory_write" in decision_agent1 and decision_agent1["memory_write"]:
            agent1.memory.write(MemoryItem(t=tick, kind="episodic", text=decision_agent1["memory_write"], importance=0.5))
        print(f"Tick {tick} - {agent1.persona.name} to: {agent2.persona.name}: {decision_agent1.get('reply', None)}")
        # Interleave: agent1 takes an action in the world
        action_decision1 = agent1.decide(world, obs_agent1, tick, start)
        agent1.act(world, action_decision1, tick)
        print(f"Tick {tick} - {agent1.persona.name} action: {action_decision1.get('action', None)}")

        incoming_message_agent2 = None
        if decision_agent1:
            incoming_message_agent2 = {
                'to': agent2.persona.name,
                'from': agent1.persona.name,
                'text': decision_agent1.get("reply", None)
            }
        # Agent 2 decides and acts
        decision_agent2 = agent2.decide_conversation(
            participants=participants,
            obs=obs_agent2, tick=tick,
            incoming_message=incoming_message_agent2, loglist=loglist
        )
        last_decision_agent2 = decision_agent2
        if decision_agent2 and "new_mood" in decision_agent2:
            agent2.physio.mood = decision_agent2["new_mood"]
        if decision_agent2 and "memory_write" in decision_agent2 and decision_agent2["memory_write"]:
            agent2.memory.write(MemoryItem(t=tick, kind="episodic", text=decision_agent2["memory_write"], importance=0.5))
        print(f"Tick {tick} - {agent2.persona.name} to: {agent1.persona.name}: {decision_agent2.get('reply', None)}")
        # Interleave: agent2 takes an action in the world
        action_decision2 = agent2.decide(world, obs_agent2, tick, start)
        agent2.act(world, action_decision2, tick)
        print(f"Tick {tick} - {agent2.persona.name} action: {action_decision2.get('action', None)}")


    # Combine conversation histories and output to a file
    import json
    def extract_message(entry):
        content = entry
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
    logs_dir = "conversation_logs"
    os.makedirs(logs_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{agent1.persona.name}_{agent2.persona.name}_door_{timestamp_str}.txt"
    filepath = os.path.join(logs_dir, filename)
    with open(filepath, 'w', encoding="utf-8") as f:
        f.write(f"----- Conversation between {agent1.persona.name} and {agent2.persona.name} (with door/padlock) -----\n\n")
        for msg in messages:
            f.write(msg + "\n\n")
    assert any(entry["role"] == "agent" for entry in agent1.conversation_history), "Agent1 did not reply during conversation."
    assert any(entry["role"] == "agent" for entry in agent2.conversation_history), "Agent2 did not reply during conversation."
    agent1_replies = [entry["content"] for entry in agent1.conversation_history if entry["role"] == "agent"]
    agent2_replies = [entry["content"] for entry in agent2.conversation_history if entry["role"] == "agent"]
    agent1_to_agent2 = any(agent2.persona.name in reply for reply in agent1_replies)
    agent2_to_agent1 = any(agent1.persona.name in reply for reply in agent2_replies)
    assert agent1_to_agent2 or agent2_to_agent1, "No direct conversation detected."
    #check if anyone tried to unlock or open the door
    door_actions = ["unlock the door", "open the door", "use the key", "try to open the door", "try to unlock the door"]
    action_texts = [action_decision1.get("action", "").lower(), action_decision2.get("action", "").lower()]
    assert any(any(da in action for da in door_actions) for action in action_texts), "No one tried to unlock or open the door."



def make_test_world():
    places = {
        "Room": Place("Room", [], set(), None, "Unknown"),
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
    for tick in range(1, 15):
        participants = [agent1, agent2]
        incoming_message_agent1 = None
        if last_decision_agent2:
            incoming_message_agent1 = {
                'to': agent1.persona.name,
                'from': agent2.persona.name,
                'text': last_decision_agent2.get("reply", None)
            }
        decision_agent1 = agent1.step_interact(world, participants, obs_agent1, tick, start, incoming_message_agent1, loglist=loglist)
        print(f"Tick {tick} - {agent1.persona.name} to: {agent2.persona.name}: {decision_agent1.get('reply', None)}")

        incoming_message_agent2 = None
        if decision_agent1:
            incoming_message_agent2 = {
                'to': agent2.persona.name,
                'from': agent1.persona.name,
                'text': decision_agent1.get("reply", None)
            }
        decision_agent2 = agent2.step_interact(world, participants, obs_agent2, tick, start, incoming_message_agent2, loglist=loglist)
        last_decision_agent2 = decision_agent2
        print(f"Tick {tick} - {agent2.persona.name} to: {agent1.persona.name}: {decision_agent2.get('reply', None)}")
    
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
        for tick in range(1, 15):
            participants = [agent1, agent2]
            incoming_message_agent1 = None
            if last_decision_agent2:
                incoming_message_agent1 = {
                    'to': agent1.persona.name,
                    'from': agent2.persona.name,
                    'text': last_decision_agent2.get("reply", None)
                }
            decision_agent1 = agent1.step_interact(world, participants, obs_agent1, tick, start, incoming_message_agent1, loglist=loglist)
            print(f"Tick {tick} - {agent1.persona.name} to: {agent2.persona.name}: {decision_agent1.get('reply', None)}")

            incoming_message_agent2 = None
            if decision_agent1:
                incoming_message_agent2 = {
                    'to': agent2.persona.name,
                    'from': agent1.persona.name,
                    'text': decision_agent1.get("reply", None)
                }
            decision_agent2 = agent2.step_interact(world, participants, obs_agent2, tick, start, incoming_message_agent2, loglist=loglist)
            last_decision_agent2 = decision_agent2
            print(f"Tick {tick} - {agent2.persona.name} to: {agent1.persona.name}: {decision_agent2.get('reply', None)}")
            print("pytest not available, running all tests directly...")
            for name, fn in test_functions.items():
                print(f"Running {name}...")
                try:
                    fn()
                    print(f"{name}: PASSED")
                except Exception as e:
                    print(f"{name}: FAILED\n{e}")