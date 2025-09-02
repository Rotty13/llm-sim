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
    def __init__(self, capacity_weight: float = 9999.0):
        self.stacks: List[ItemStack] = []
        self.capacity_weight = capacity_weight

    def _current_weight(self) -> float:
        return sum(s.item.weight * s.qty for s in self.stacks)

    def can_add(self, item: Item, qty: int = 1) -> bool:
        return self._current_weight() + item.weight * qty <= self.capacity_weight

    def add(self, item: Item, qty: int = 1) -> bool:
        if not self.can_add(item, qty): return False
        for s in self.stacks:
            if s.item.id == item.id:
                s.qty += qty
                return True
        self.stacks.append(ItemStack(item, qty))
        return True

    def has(self, item_id: str, qty: int = 1) -> bool:
        total = 0
        for s in self.stacks:
            if s.item.id == item_id:
                total += s.qty
                if total >= qty: return True
        return False

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
        return sum(s.qty for s in self.stacks if s.item.id == item_id)

    def to_compact_str(self) -> str:
        return ", ".join(f"{s.item.name} x{s.qty}" for s in self.stacks) or "(empty)"

ITEMS = {
    "money":   Item(id="money",   name="$",        tags={"currency"},                    weight=0.0, effects={}),
    "coffee":  Item(id="coffee",  name="Coffee",   tags={"edible","drink","caffeine"},   weight=0.1, effects={"hunger": -0.2, "energy": +0.15, "stress": -0.02}),
    "pastry":  Item(id="pastry",  name="Pastry",   tags={"edible","food","carb"},        weight=0.2, effects={"hunger": -0.45, "energy": +0.05}),
    "salad":   Item(id="salad",   name="Salad",    tags={"edible","food"},               weight=0.3, effects={"hunger": -0.5, "stress": -0.02}),
    "beans":   Item(id="beans",   name="Coffee Beans", tags={"ingredient"},              weight=0.5, effects={}),
    "sketch":  Item(id="sketch",  name="Sketch",   tags={"art","sellable"},              weight=0.0, effects={}),
}
