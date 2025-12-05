"""
Pytest-based tests for commerce mechanics in the Vendor class.
"""
import pytest
from sim.world.world import Vendor
from sim.inventory.inventory import Item, ITEMS
from sim.agents.agents import Agent, Persona

@pytest.fixture
def vendor_and_agent():
    vendor = Vendor(
        prices={"coffee": 5},
        stock={"coffee": 10},
        buyback={"coffee": 2}
    )
    persona = Persona(name="Alice", age=30, job="developer", city="TestCity", bio="Test bio", values=[], goals=[])
    agent = Agent(persona=persona, place="Cafe")
    if agent.inventory is not None:
        agent.inventory.add(ITEMS["money"], 50)  # Add initial money
        agent.inventory.add(ITEMS["coffee"], 2)  # Add initial coffee
    return vendor, agent

def test_buy_item_success(vendor_and_agent):
    vendor, agent = vendor_and_agent
    assert vendor.buy("coffee", 2, agent)
    if agent.inventory is not None:
        assert agent.inventory.get_quantity("coffee") == 4
        assert agent.inventory.get_quantity("money") == 40
    assert vendor.stock["coffee"] == 8

def test_buy_item_insufficient_stock(vendor_and_agent):
    vendor, agent = vendor_and_agent
    assert not vendor.buy("coffee", 20, agent)
    if agent.inventory is not None:
        assert agent.inventory.get_quantity("coffee") == 2
        assert agent.inventory.get_quantity("money") == 50

def test_buy_item_insufficient_money(vendor_and_agent):
    vendor, agent = vendor_and_agent
    if agent.inventory is not None:
        agent.inventory.remove("money", 50)  # Remove all money
    assert not vendor.buy("coffee", 2, agent)
    if agent.inventory is not None:
        assert agent.inventory.get_quantity("coffee") == 2
    assert vendor.stock["coffee"] == 10

def test_sell_item_success(vendor_and_agent):
    vendor, agent = vendor_and_agent
    assert vendor.sell("coffee", 1, agent)
    if agent.inventory is not None:
        assert agent.inventory.get_quantity("coffee") == 1
        assert agent.inventory.get_quantity("money") == 52
    assert vendor.stock["coffee"] == 11

def test_sell_item_insufficient_quantity(vendor_and_agent):
    vendor, agent = vendor_and_agent
    if agent.inventory is not None:
        agent.inventory.remove("coffee", 2)  # Remove all coffee
    assert not vendor.sell("coffee", 1, agent)
    if agent.inventory is not None:
        assert agent.inventory.get_quantity("money") == 50
    assert vendor.stock["coffee"] == 10

def test_sell_item_no_buyback(vendor_and_agent):
    vendor, agent = vendor_and_agent
    vendor.buyback.pop("coffee")  # Remove buyback price
    assert not vendor.sell("coffee", 1, agent)
    if agent.inventory is not None:
        assert agent.inventory.get_quantity("coffee") == 2
        assert agent.inventory.get_quantity("money") == 50