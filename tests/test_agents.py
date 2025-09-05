from __future__ import annotations
from datetime import datetime
from sim.world.world import World, Place, Vendor
from sim.agents.agents import Agent, Persona, Appointment, now_str
from sim.memory.memory import MemoryItem

# ---------- Shared test helpers ----------

def make_world(include_park=False):
    places = {
        "Street":  Place("Street",  ["Apartment","Cafe","Office"], set(), None, "Main road"),
        "Apartment": Place("Apartment", ["Street"], {"sleep","food_home"}, None, "Home"),
        "Cafe":    Place("Cafe",    ["Street"], {"food","coffee"},
                         vendor=Vendor(prices={"coffee":3.5}, stock={"coffee":999}), purpose="Cafe"),
        "Office":  Place("Office",  ["Street"], {"work_dev"}, None, "Work"),
    }
    if include_park:
        places["Park"] = Place("Park", ["Street"], {"park"}, None, "Green space")
        # allow Street to reach Park in this test world
        places["Street"].neighbors.append("Park")
    return World(places=places)

def make_agents(city="Redwood"):
    a = Agent(
        persona=Persona(
            name="Lily Tran", age=27, job="barista", city=city,
            bio="Loves latte art.", values=["kindness","creativity","stability"],
            goals=["pay rent","improve latte art","make friends"]
        ),
        place="Apartment",
        calendar=[Appointment(at_min=0, place="Cafe", label="shift")],
    )
    b = Agent(
        persona=Persona(
            name="Ethan Kim", age=31, job="junior dev", city=city,
            bio="New in town.", values=["learning","honesty","security"],
            goals=["keep new job","save money","meet people"]
        ),
        place="Street",
        calendar=[Appointment(at_min=60, place="Office", label="standup")],
    )
    return [a, b]

def run_ticks(world: World, agents: list[Agent], ticks: int):
    """Minimal driver (mirrors your run_sim loop)"""
    world._agents = agents
    start = datetime(2025, 8, 31, 9, 0, 0)
    for t in range(1, ticks+1):
        perceptions = {}
        for ag in agents:
            obs = []
            for evt in list(world.events):
                if evt.get("place")==ag.place and evt.get("actor")!=ag.persona.name:
                    kind, text = evt.get("kind"), evt.get("text","")
                    obs.append(f"{evt['actor']} {kind} {text}")
            perceptions[ag.persona.name] = "; ".join(obs) if obs else "(quiet)"
        for ag in agents:
            dec = ag.decide(world, perceptions[ag.persona.name], t, start)
            ag.act(world, dec, t)
    return start

# ---------- Tests ----------

def test_personality_consistency_autobio_mentions_values():
    """Agent diaries should reflect their stated values over time."""
    world = make_world()
    [lily, ethan] = make_agents()
    start = run_ticks(world, [lily, ethan], ticks=12)

    lily_diary = [m.text.lower() for m in lily.memory.items if m.kind=="autobio"]
    # With our stub, Lily often THINK/SAY about social/creative intent
    # Check that at least one diary line hints at social/creativity themes
    hit = any(any(k in d for k in ("friend","social","create","art","kind")) for d in lily_diary)
    assert hit, f"Lily diary lacked personality cues: {lily_diary}"


def test_autonomy_idle_does_not_freeze():
    """With no explicit external trigger, agents should still produce non-THINK actions sometimes."""
    world = make_world()
    [lily, ethan] = make_agents()
    run_ticks(world, [lily, ethan], ticks=10)

    kinds = [evt.get("text","") for evt in world.events if evt.get("actor")==lily.persona.name and evt.get("kind")=="act"]
    # Expect at least one non-THINK (e.g., EAT/WORK/PLAN) from the stub rule
    assert any(not s.startswith("THINK") for s in kinds), f"Only THINK actions found: {kinds}"


def test_memory_influences_behavior_and_recall():
    """Seed a semantic memory and ensure it shows up in recall-driven prompt usage (via diaries/actions)."""
    world = make_world()
    [lily, ethan] = make_agents()
    # Seed important semantic memory
    lily.memory.write(MemoryItem(t=0, kind="semantic", text="Rent is due on the 1st.", importance=0.9))

    run_ticks(world, [lily, ethan], ticks=12)

    # We can't directly read the internal prompt, so we assert downstream effects:
    # - some autobio lines referencing rent / money / budget appear
    diary = " ".join(m.text.lower() for m in lily.memory.items if m.kind=="autobio")
    assert any(k in diary for k in ("rent","budget","pay")), f"No rent-related reflection found: {diary}"


def test_curiosity_explores_new_place():
    """If a new place exists and we hint exploration, the stub moves there at least once."""
    world = make_world(include_park=True)
    [lily, ethan] = make_agents()
    world._agents = [lily, ethan]
    start = datetime(2025, 8, 31, 9, 0, 0)

    # Manually drive one tick with an exploration tag in the prompt by calling decide() directly.
    obs = "(quiet)"
    # We piggyback on the decide() prompt content by extending needs line:
    # easiest way: call decide(), then overwrite the prompt via monkeypatching is complex.
    # Instead, briefly move Lily to Street (neighbor of Park) and trick the stub:
    lily.place = "Street"
    # Call decide with a crafted observation that contains our tag the stub looks for.
    # We don't have direct prompt injection, but we can simulate by temporarily monkeypatching
    # Agent.decide to append the tag. To keep this test simple, we call the LLM stub directly:
    from sim.llm.llm import llm as stub_llm
    out = stub_llm.chat_json("curiosity:explore\nLocation Street\nNeeds: energy=0.80, hunger=0.20, stress=0.10", system="", max_tokens=128)
    lily.act(world, out, tick=1)

    # Confirm a MOVE to Park happened (or Lily is now at Park)
    moved_to_park = any(evt for evt in world.events if evt.get("actor")==lily.persona.name and "Park" in evt.get("text",""))
    assert moved_to_park or lily.place == "Park", "Agent did not explore the new Park"


def test_desires_social_agent_speaks_more():
    """Agent with 'make friends' should produce more SAY than the more work-focused dev."""
    world = make_world()
    [lily, ethan] = make_agents()
    run_ticks(world, [lily, ethan], ticks=18)

    lily_says = sum(1 for e in world.events if e.get("actor")==lily.persona.name and e.get("kind")=="say")
    ethan_says = sum(1 for e in world.events if e.get("actor")==ethan.persona.name and e.get("kind")=="say")
    assert lily_says >= ethan_says, f"Expected Lily to be more social: lily={lily_says}, ethan={ethan_says}"


def test_schedule_enforcement_autonomy():
    """Ethan has a stand-up at +60min (tick 12). Ensure he ends up at Office around then."""
    world = make_world()
    [lily, ethan] = make_agents()
    start = run_ticks(world, [lily, ethan], ticks=14)  # > 60 minutes at 5-min ticks

    # Look for an event around tick ~12 that moved Ethan to Office, or that he's at Office at end
    ethan_moves = [e for e in world.events if e.get("actor")==ethan.persona.name and e.get("kind")=="move"]
    moved_to_office = any("Office" in e.get("text","") for e in ethan_moves)
    assert moved_to_office or ethan.place == "Office", "Ethan didn't reach Office for the stand-up"
