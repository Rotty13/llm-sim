"""
Manages inventory-related operations for an agent.

Classes:
    InventoryHandler: Handles inventory interactions such as deposit, withdrawal, and usage.

Methods:
    deposit_item(place, item_id: str, qty: int = 1): Deposits an item to a place's inventory.
    withdraw_item(place, item_id: str, qty: int = 1): Withdraws an item from a place's inventory.
    use_item(item): Uses an item from the inventory.
    deposit_item_to_place(agent, world, item_id: str, qty: int = 1): Deposits an item from the agent's inventory to the current place's inventory.
    withdraw_item_from_place(agent, world, item_id: str, qty: int = 1): Withdraws an item from the current place's inventory to the agent's inventory.
"""

from sim.inventory.inventory import Inventory
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class InventoryHandler:
    """
    Manages inventory-related operations for an agent.
    """
    def __init__(self, capacity_weight: float = 5.0):
        self.inventory = Inventory(capacity_weight=capacity_weight)
        self.ownership_log = []  # Track ownership changes

    def log_ownership_change(self, action: str, item_id: str, qty: int, agent, place):
        """
        Log ownership changes when items are deposited or withdrawn.
        """
        entry = {
            "action": action,
            "item_id": item_id,
            "quantity": qty,
            "agent": agent.persona.name,
            "place": place.name
        }
        self.ownership_log.append(entry)
        logger.info(f"Ownership change logged: {entry}")

    def deposit_item(self, place, item_id: str, qty: int = 1, agent=None) -> bool:
        """
        Deposit an item from the agent's inventory to a place's inventory.
        Validates permissions and capacity before proceeding.
        """
        logger.debug(f"Checking if inventory has item {item_id} (qty: {qty}).")
        if not self.inventory.has(item_id, qty):
            logger.error(f"Item {item_id} (qty: {qty}) not found in inventory.")
            return False

        # Validate place capacity
        if place.inventory.get_total_weight() + (self.inventory.get_item_weight(item_id) * qty) > place.inventory.capacity_weight:
            logger.error(f"Place {place.name} cannot accommodate item {item_id} due to weight capacity.")
            return False

        logger.debug(f"Item {item_id} found in inventory. Attempting to deposit.")
        item_stack = next((s for s in self.inventory.stacks if s.item.id == item_id), None)
        if item_stack:
            item = item_stack.item
            if self.inventory.remove(item_id, qty):
                logger.debug(f"Item {item_id} removed from inventory. Adding to place inventory.")
                place.inventory.add(item, qty)
                if agent:
                    self.log_ownership_change("deposit", item_id, qty, agent, place)
                return True
            else:
                logger.error(f"Failed to remove item {item_id} from inventory.")
        return False

    def withdraw_item(self, place, item_id: str, qty: int = 1, agent=None) -> bool:
        """
        Withdraw an item from a place's inventory to the agent's inventory.
        Validates permissions and agent capacity before proceeding.
        """
        item_stack = next((s for s in place.inventory.stacks if s.item.id == item_id), None)
        if not item_stack or item_stack.qty < qty:
            logger.error(f"Item {item_id} (qty: {qty}) not available in place {place.name}.")
            return False

        # Validate agent capacity
        if self.inventory.get_total_weight() + (place.inventory.get_item_weight(item_id) * qty) > self.inventory.capacity_weight:
            logger.error(f"Agent cannot carry item {item_id} due to weight capacity.")
            return False

        if place.inventory.remove(item_id, qty):
            self.inventory.add(item_stack.item, qty)
            if agent:
                self.log_ownership_change("withdraw", item_id, qty, agent, place)
            return True
        return False

    def use_item(self, item) -> bool:
        """
        Use an item from the inventory.
        """
        if self.inventory.has(item.id):
            self.inventory.remove(item.id, 1)
            return True
        return False

    def deposit_item_to_place(self, agent, world, item_id: str, qty: int = 1) -> bool:
        """
        Deposit an item from the agent's inventory to the current place's inventory.
        """
        logger.debug(f"Attempting to deposit item {item_id} (qty: {qty}) from agent {agent.persona.name} at place {agent.place}.")
        if agent.place not in world.places:
            logger.error(f"Place {agent.place} not found in world.")
            return False
        place = world.places[agent.place]
        result = self.deposit_item(place, item_id, qty, agent)
        logger.debug(f"Deposit result: {result}")
        return result

    def withdraw_item_from_place(self, agent, world, item_id: str, qty: int = 1) -> bool:
        """
        Withdraw an item from the current place's inventory to the agent's inventory.
        """
        logger.debug(f"Attempting to withdraw item {item_id} (qty: {qty}) to agent {agent.persona.name} at place {agent.place}.")
        if agent.place not in world.places:
            logger.error(f"Place {agent.place} not found in world.")
            return False
        place = world.places[agent.place]
        result = self.withdraw_item(place, item_id, qty, agent)
        logger.debug(f"Withdraw result: {result}")
        return result