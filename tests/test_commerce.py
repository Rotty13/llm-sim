"""
Unit tests for commerce mechanics in the Vendor class.
"""
import unittest
from sim.world.world import Vendor
from sim.inventory.inventory import Item, ITEMS
from sim.agents.agents import Agent, Persona

class TestCommerceMechanics(unittest.TestCase):

    def setUp(self):
        self.vendor = Vendor(
            prices={"coffee": 5},
            stock={"coffee": 10},
            buyback={"coffee": 2}
        )
        persona = Persona(name="Alice", age=30, job="developer", city="TestCity", bio="Test bio", values=[], goals=[])
        self.agent = Agent(persona=persona, place="Cafe")
        self.agent.inventory.add(ITEMS["money"], 50)  # Add initial money
        self.agent.inventory.add(ITEMS["coffee"], 2)  # Add initial coffee

    def test_buy_item_success(self):
        self.assertTrue(self.vendor.buy("coffee", 2, self.agent))
        self.assertEqual(self.agent.inventory.get_quantity("coffee"), 4)
        self.assertEqual(self.agent.inventory.get_quantity("money"), 40)
        self.assertEqual(self.vendor.stock["coffee"], 8)

    def test_buy_item_insufficient_stock(self):
        self.assertFalse(self.vendor.buy("coffee", 20, self.agent))
        self.assertEqual(self.agent.inventory.get_quantity("coffee"), 2)
        self.assertEqual(self.agent.inventory.get_quantity("money"), 50)

    def test_buy_item_insufficient_money(self):
        self.agent.inventory.remove("money", 50)  # Remove all money
        self.assertFalse(self.vendor.buy("coffee", 2, self.agent))
        self.assertEqual(self.agent.inventory.get_quantity("coffee"), 2)
        self.assertEqual(self.vendor.stock["coffee"], 10)

    def test_sell_item_success(self):
        self.assertTrue(self.vendor.sell("coffee", 1, self.agent))
        self.assertEqual(self.agent.inventory.get_quantity("coffee"), 1)
        self.assertEqual(self.agent.inventory.get_quantity("money"), 52)
        self.assertEqual(self.vendor.stock["coffee"], 11)

    def test_sell_item_insufficient_quantity(self):
        self.agent.inventory.remove("coffee", 2)  # Remove all coffee
        self.assertFalse(self.vendor.sell("coffee", 1, self.agent))
        self.assertEqual(self.agent.inventory.get_quantity("money"), 50)
        self.assertEqual(self.vendor.stock["coffee"], 10)

    def test_sell_item_no_buyback(self):
        self.vendor.buyback.pop("coffee")  # Remove buyback price
        self.assertFalse(self.vendor.sell("coffee", 1, self.agent))
        self.assertEqual(self.agent.inventory.get_quantity("coffee"), 2)
        self.assertEqual(self.agent.inventory.get_quantity("money"), 50)

if __name__ == "__main__":
    unittest.main()