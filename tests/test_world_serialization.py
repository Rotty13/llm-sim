"""
test_world_serialization.py

Pytest function for World YAML serialization and deserialization.
"""
import os
import tempfile
from collections import deque
from sim.world.world import World, Place, Vendor
from sim.agents.persona import Persona
from sim.agents.agents import Agent
from sim.inventory.inventory import Inventory, ITEMS

def test_world_yaml_serialization():
    # Create a simple world
    vendor = Vendor(prices={"coffee": 2.5}, stock={"coffee": 10}, buyback={"coffee": 1.0})
    place = Place(name="Cafe", neighbors=[], capabilities={"work", "food"}, vendor=vendor)
    persona = Persona(name="Alice", age=30, job="barista", city="TestCity", bio="", values=["kindness"], goals=["serve coffee"])
    agent = Agent(persona=persona, place="Cafe")
    world = World(places={"Cafe": place}, events=deque(["open", "close"]))
    world.add_agent(agent)
    world.set_agent_location(agent, "Cafe")
    assert agent.inventory is not None
    # Give agent some inventory
    agent.inventory.add(ITEMS["coffee"], 2)
    # Serialize to YAML
    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tmp:
        yaml_path = tmp.name
    world.save_state_yaml(yaml_path)
    # Load from YAML
    loaded = World.load_state_yaml(yaml_path)
    os.remove(yaml_path)
    # Assertions
    assert "Cafe" in loaded.places
    assert loaded.get_all_agents()[0].persona.name == "Alice"
    assert loaded.get_all_agents()[0].inventory.has("coffee", 2)
    assert list(loaded.events) == ["open", "close"]
    assert loaded.get_agent_location("Alice") == "Cafe"
