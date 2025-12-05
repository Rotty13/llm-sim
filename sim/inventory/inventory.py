"""
inventory.py

Defines Item, ItemStack, and Inventory classes for agent and place inventory management in llm-sim.
Supports item addition, removal, quantity tracking, and tag-based search.

Key Classes:
- Item: Represents an individual item with id, name, tags, weight, and effects.
- ItemStack: Associates an Item with a quantity.
- Inventory: Manages collections of ItemStacks, supporting add/remove/check operations.

Key Functions:
- interact_with_inventory: Stub for item-inventory interaction.
- interact_with_place: Stub for item-place interaction.
- interact_with_vendor: Stub for item-vendor interaction.

LLM Usage:
- None directly; inventory logic may be used by agent/world modules that interact with LLMs.

CLI Arguments:
- None directly; inventory objects are managed by simulation scripts and agent logic.
"""

from typing import Any
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def interact_with_inventory(self, inventory: 'Inventory', qty: int = 1):
        """Stub: Item interacts with inventory (add/remove/check)."""
        pass

def interact_with_place(self, place: Any, qty: int = 1):
        """Stub: Item interacts with a place (deposit/withdraw)."""
        pass

def interact_with_vendor(self, vendor: Any, qty: int = 1, buy: bool = True):
        """Stub: Item interacts with vendor (buy/sell)."""
        pass
"""
inventory.py

Defines Item, ItemStack, and Inventory classes for agent and place inventory management in llm-sim.
Supports item addition, removal, quantity tracking, and tag-based search.

Key Classes:
- Item: Represents an individual item with id, name, tags, weight, and effects.
- ItemStack: Associates an Item with a quantity.
- Inventory: Manages collections of ItemStacks, supporting add/remove/check operations.

Key Functions:
- interact_with_inventory: Stub for item-inventory interaction.
- interact_with_place: Stub for item-place interaction.
- interact_with_vendor: Stub for item-vendor interaction.

LLM Usage:
- None directly; inventory logic may be used by agent/world modules that interact with LLMs.

CLI Arguments:
- None directly; inventory objects are managed by simulation scripts and agent logic.
"""

# Inventory classes and items
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set

@dataclass(frozen=True)
class Item:
    id: str
    name: str
    tags: Set[str]
    weight: float = 0.0
    effects: Optional[Dict[str, float]] = None

@dataclass
class ItemStack:
    item: Item
    qty: int = 1

class Inventory:
    def serialize(self) -> list:
        """
        Serialize inventory to a list of dicts: [{"item_id": ..., "qty": ...}, ...]
        """
        return [{"item_id": s.item.id, "qty": s.qty} for s in self.stacks]

    def load(self, data: list):
        """
        Load inventory from a list of dicts: [{"item_id": ..., "qty": ...}, ...]
        """
        self.stacks.clear()
        for entry in data:
            item_id = entry.get("item_id")
            qty = entry.get("qty", 1)
            if item_id in ITEMS:
                self.stacks.append(ItemStack(ITEMS[item_id], qty))
    def __init__(self, capacity_weight: float = 9999.0):
        self.stacks: List[ItemStack] = []
        self.capacity_weight = capacity_weight

    def _current_weight(self) -> float:
        return sum(s.item.weight * s.qty for s in self.stacks)

    def can_add(self, item: Item, qty: int = 1) -> bool:
        return self._current_weight() + item.weight * qty <= self.capacity_weight

    def add(self, item: Item, qty: int = 1) -> bool:
        logger.debug(f"Attempting to add item {item} (qty: {qty}) to inventory.")
        if not self.can_add(item, qty):
            logger.error(f"Cannot add item {item.id} (qty: {qty}). Exceeds capacity.")
            return False
        for s in self.stacks:
            logger.debug(f"Inspecting stack during add: {s.item} (qty: {s.qty}).")
            if s.item.id == item.id:
                s.qty += qty
                logger.debug(f"Updated existing stack for item {item.id}. New quantity: {s.qty}.")
                return True
        self.stacks.append(ItemStack(item, qty))
        logger.debug(f"Added new stack for item {item}. Quantity: {qty}.")
        return True

    def has(self, item_id: str, qty: int = 1) -> bool:
        logger.debug(f"Checking if inventory contains item {item_id} (qty: {qty}).")
        total = self.count(item_id)
        logger.debug(f"Total quantity of {item_id} in inventory: {total}.")
        return total >= qty

    def remove(self, item_id: str, qty: int = 1) -> bool:
        needed = qty
        for s in list(self.stacks):
            if s.item.id == item_id:
                take = min(s.qty, needed)
                s.qty -= take
                needed -= take
                if s.qty <= 0: self.stacks.remove(s)
                if needed <= 0: return True
        return False

    def find_by_tag(self, tag: str) -> Optional[ItemStack]:
        for s in self.stacks:
            if tag in s.item.tags and s.qty > 0:
                return s
        return None

    def count(self, item_id: str) -> int:
        logger.debug(f"Counting total quantity of item {item_id} in inventory.")
        total = 0
        for s in self.stacks:
            logger.debug(f"Inspecting stack: {s.item.id} (qty: {s.qty}).")
            if s.item.id == item_id:
                total += s.qty
                logger.debug(f"Running total for {item_id}: {total}.")
        logger.debug(f"Final total quantity of {item_id}: {total}.")
        return total

    def to_compact_str(self) -> str:
        return ", ".join(f"{s.item.name} x{s.qty}" for s in self.stacks) or "(empty)"

    def get_quantity(self, item_id: str) -> int:
        """
        Get the total quantity of an item in the inventory by its ID.
        """
        return sum(s.qty for s in self.stacks if s.item.id == item_id)

    def get_item_weight(self, item_id: str) -> float:
        """
        Get the weight of a single unit of the specified item.
        """
        for s in self.stacks:
            if s.item.id == item_id:
                return s.item.weight
        raise ValueError(f"Item {item_id} not found in inventory.")

    def get_total_weight(self) -> float:
        """
        Calculate the total weight of all items in the inventory.
        """
        return self._current_weight()

ITEMS = {
    "money":   Item(id="money",   name="$",        tags={"currency"},                    weight=0.0, effects={}),
    "coffee":  Item(id="coffee",  name="Coffee",   tags={"edible","drink","caffeine"},   weight=0.1, effects={"hunger": -0.2, "energy": +0.15, "stress": -0.02}),
    "pastry":  Item(id="pastry",  name="Pastry",   tags={"edible","food","carb"},        weight=0.2, effects={"hunger": -0.45, "energy": +0.05}),
    "salad":   Item(id="salad",   name="Salad",    tags={"edible","food"},               weight=0.3, effects={"hunger": -0.5, "stress": -0.02}),
    "beans":   Item(id="beans",   name="Coffee Beans", tags={"ingredient"},              weight=0.5, effects={}),
    "sketch":  Item(id="sketch",  name="Sketch",   tags={"art","sellable"},              weight=0.0, effects={}),
    "apple":   Item(id="apple",   name="Apple",    tags={"edible","food","fruit"},      weight=0.15, effects={"hunger": -0.3, "energy": +0.02}),
}
