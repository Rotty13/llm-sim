from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from collections import deque

@dataclass
class Vendor:
    prices: Dict[str, float] = field(default_factory=dict)   # item_id -> price
    stock: Dict[str, int] = field(default_factory=dict)      # item_id -> qty
    buyback: Dict[str, float] = field(default_factory=dict)  # item_id -> price

    def has(self, item_id: str, qty: int = 1) -> bool:
        return self.stock.get(item_id, 0) >= qty

    def take(self, item_id: str, qty: int = 1) -> bool:
        if not self.has(item_id, qty): return False
        self.stock[item_id] -= qty
        return True

@dataclass
class Place:
    name: str
    neighbors: List[str]
    capabilities: set[str] = field(default_factory=set)
    vendor: Optional[Vendor] = None
    purpose: str = ""

@dataclass
class World:
    places: Dict[str, Place]
    events: deque = field(default_factory=deque)

    def broadcast(self, place: str, payload: Dict[str, Any]):
        self.events.append({"place": place, **payload})
        # hard cap
        if len(self.events) > 512:
            for _ in range(128):
                self.events.popleft()

    def valid_place(self, name: str) -> bool:
        return name in self.places

ALLOWED_CAPS = {"sleep","food_home","food","coffee","work_dev","park","shop","bar","gallery","transit","gym","school"}

