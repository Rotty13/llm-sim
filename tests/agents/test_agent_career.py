"""
test_agent_career.py

Automated tests for agent career, job progression, and economy interactions.
"""
import pytest
from sim.agents.persona import Persona
from sim.agents.agents import Agent
from sim.agents.modules.agent_actions import AgentActions
from sim.inventory.inventory import ITEMS

class DummyVendor:
    def __init__(self):
        self.stock = {"pastry": 10}
    def sell(self, item_id, qty):
        if self.stock.get(item_id, 0) >= qty:
            self.stock[item_id] -= qty
            return ITEMS[item_id]
        return None
    def buy(self, item_id, qty):
        self.stock[item_id] = self.stock.get(item_id, 0) + qty
        return True
    def add_item(self, item_id, qty):
        self.stock[item_id] = self.stock.get(item_id, 0) + qty

class DummyPlace:
    def __init__(self):
        self.inventory = DummyVendor()

@pytest.fixture
def agent_baker():
    persona = Persona(name="Alice", age=30, job="baker", city="Testville", bio="Baker", values=[], goals=[])
    agent = Agent(persona=persona)
    agent.actions = AgentActions()
    return agent

def test_work_at_place_produces_pastry(agent_baker):
    place = "Bakery"
    agent_baker.place = place
    result = agent_baker.work_at_place(place, None, 0)
    assert result
    assert agent_baker.inventory.has_item("pastry")

def test_buy_from_vendor(agent_baker):
    vendor = DummyVendor()
    result = agent_baker.buy_from_vendor(vendor, "pastry", 2)
    assert result
    assert agent_baker.inventory.has_item("pastry")
    assert agent_baker.inventory.get_quantity("pastry") >= 2

def test_sell_to_vendor(agent_baker):
    vendor = DummyVendor()
    agent_baker.inventory.add_item(ITEMS["pastry"], 3)
    result = agent_baker.sell_to_vendor(vendor, "pastry", 2)
    assert result
    assert agent_baker.inventory.get_quantity("pastry") == 1
    assert vendor.stock["pastry"] == 12

def test_interact_with_inventory(agent_baker):
    other_inventory = DummyVendor()
    agent_baker.inventory.add_item(ITEMS["pastry"], 2)
    result = agent_baker.interact_with_inventory(other_inventory, "pastry", 1)
    assert result
    assert agent_baker.inventory.get_quantity("pastry") == 1
    assert other_inventory.stock["pastry"] == 11

def test_interact_with_place(agent_baker):
    place = DummyPlace()
    agent_baker.inventory.add_item(ITEMS["pastry"], 1)
    result = agent_baker.interact_with_place(place, "pastry", 1)
    assert result
    assert agent_baker.inventory.get_quantity("pastry") == 0
    assert place.inventory.stock["pastry"] == 11
