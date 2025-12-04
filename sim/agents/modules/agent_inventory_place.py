"""
AgentInventoryPlace module for managing inventory deposit and withdrawal to/from places.
Handles item transfer between agent and place inventories.
"""
from sim.inventory.inventory import ITEMS

class AgentInventoryPlace:
    def __init__(self, inventory):
        self.inventory = inventory

    def deposit_item_to_place(self, world, place, item_name, quantity):
        if self.inventory and self.inventory.get_quantity(item_name) >= quantity:
            self.inventory.remove_item(item_name, quantity)
            place_obj = world.places[place]
            item_obj = ITEMS[item_name]
            if hasattr(place_obj, 'inventory') and hasattr(place_obj.inventory, 'add'):
                place_obj.inventory.add(item_obj, quantity)
                return True
        return False

    def withdraw_item_from_place(self, world, place, item_name, quantity):
        place_obj = world.places[place]
        if hasattr(place_obj, 'inventory') and place_obj.inventory.get_quantity(item_name) >= quantity:
            place_obj.inventory.remove(item_name, quantity)
            item_obj = ITEMS[item_name]
            if self.inventory:
                self.inventory.add_item(item_name, quantity)
                return True
        return False
