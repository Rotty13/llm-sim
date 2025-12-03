"""
Place class for llm-sim world simulation.

Encapsulates location attributes, agent presence, inventory, affordances, and extensibility for future features.

Key Features:
- Name, description, type, affordances
- Inventory for items (expects Item objects)
- List of present agents
- Extensible for events, metrics, commerce, etc.
- Schema validation recommended for config integration

LLM Usage:
- No direct LLM calls; integrates with agent/world logic that may use LLMs.

CLI Arguments:
- None directly; Place objects are loaded via world configs and scripts.

"""
from __future__ import annotations
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from sim.inventory.inventory import Inventory

@dataclass
class Place:
    name: str
    description: str = ""
    place_type: str = "generic"
    affordances: List[str] = field(default_factory=list)
    inventory: Inventory = field(default_factory=Inventory)
    agents_present: List[str] = field(default_factory=list)  # agent IDs or names
    attributes: Dict[str, Any] = field(default_factory=dict)

    def add_agent(self, agent_id: str):
        if agent_id not in self.agents_present:
            self.agents_present.append(agent_id)

    def remove_agent(self, agent_id: str):
        if agent_id in self.agents_present:
            self.agents_present.remove(agent_id)

    def has_agent(self, agent_id: str) -> bool:
        return agent_id in self.agents_present

    def add_item(self, item_id: str, qty: int = 1):
        from sim.inventory.inventory import ITEMS
        item = ITEMS.get(item_id)
        if item is None:
            raise ValueError(f"Item '{item_id}' not found in ITEMS.")
        self.inventory.add(item, qty)

    def remove_item(self, item_id: str, qty: int = 1):
        self.inventory.remove(item_id, qty)

    def has_item(self, item_id: str, qty: int = 1) -> bool:
        return self.inventory.has(item_id, qty)

    def describe(self) -> str:
        return f"{self.name}: {self.description} (Type: {self.place_type})"

    # Extend with event handling, metrics, commerce, etc. as needed
