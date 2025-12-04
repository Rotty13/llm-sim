"""
Pytest-based tests for agent behavior, including movement, memory, and decision logic.
"""
import pytest
from sim.agents.agents import Agent, Persona, Physio
from sim.inventory.inventory import Item, ITEMS
from sim.world.world import World, Place
from sim.memory.memory import MemoryItem
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def setup_agent():
    place = Place(name="Cafe", neighbors=[], capabilities={"food"})
    world = World(places={"Cafe": place})
    persona = Persona(name="Bob", age=25, job="barista", city="TestCity", bio="Bio", values=["kindness"], goals=["serve coffee"])
    agent = Agent(persona=persona, place="Cafe")
    from sim.agents.memory_manager import MemoryManager
    agent.memory_manager = MemoryManager()
    from sim.agents.inventory_handler import InventoryHandler
    agent.inventory_handler = InventoryHandler()
    if not hasattr(agent, "inventory") or agent.inventory is None:
        from sim.agents.modules.agent_inventory import AgentInventory
        agent.inventory = AgentInventory()
    if not hasattr(agent, "memory") or agent.memory is None:
        from sim.agents.modules.agent_memory import AgentMemory
        agent.memory = AgentMemory()
    world._agents.append(agent)
    world.set_agent_location(agent, "Cafe")
    place.add_agent(agent)
    coffee = ITEMS["coffee"]
    agent.inventory.add(coffee, 2)
    return agent, world, place, coffee

def test_agent_memory_write(setup_agent):
    agent, world, place, coffee = setup_agent
    memory_item = MemoryItem(t=0, kind="episodic", text="Test memory", importance=0.5)
    assert agent.memory_manager is not None
    agent.memory_manager.write_memory(memory_item)
    memories = agent.memory_manager.recall_memories("test memory", k=1)
    assert any("test memory" in getattr(m, "text", "") for m in memories)

def test_agent_decision(setup_agent):
    agent, world, place, coffee = setup_agent
    decision = agent.decide(world, "see coffee", 0, None)
    assert "action" in decision
    assert "private_thought" in decision

def test_agent_move_and_use_item(setup_agent):
    agent, world, place, coffee = setup_agent
    assert agent.place == "Cafe"
    hunger_before = getattr(agent.physio, "hunger", 0.0)
    assert agent.use_item(coffee)
    hunger_after = getattr(agent.physio, "hunger", 0.0)
    if isinstance(hunger_before, (int, float)) and isinstance(hunger_after, (int, float)):
        assert hunger_after < hunger_before

def test_deposit_item_to_place(setup_agent):
    agent, world, place, coffee = setup_agent
    from sim.agents import world_interactions
    assert agent.inventory_handler is not None
    assert agent.inventory is not None
    assert world_interactions.deposit_item_to_place(agent, world, "coffee", 1)
    assert place.inventory.get_quantity("coffee") == 1
    assert agent.inventory.get_quantity(coffee.id) == 1

def test_withdraw_item_from_place(setup_agent):
    agent, world, place, coffee = setup_agent
    from sim.agents import world_interactions
    assert agent.inventory_handler is not None
    assert agent.inventory is not None
    world_interactions.deposit_item_to_place(agent, world, "coffee", 1)
    assert world_interactions.withdraw_item_from_place(agent, world, "coffee", 1)
    assert place.inventory.get_quantity("coffee") == 0
    assert agent.inventory.get_quantity(coffee.id) == 2
