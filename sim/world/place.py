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
class Area:
    name: str
    description: str = ""
    inventory: Inventory = field(default_factory=Inventory)
    agents_present: List[str] = field(default_factory=list)  # agent IDs or names
    properties: Dict[str, Any] = field(default_factory=dict)

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
        return f"{self.name}: {self.description} (Area)"

    # Extend with event handling, metrics, etc. as needed

@dataclass
class Place:
    name: str
    description: str = ""
    place_type: str = "generic"
    affordances: List[str] = field(default_factory=list)
    inventory: Inventory = field(default_factory=Inventory)
    agents_present: List[str] = field(default_factory=list)  # agent IDs or names
    attributes: Dict[str, Any] = field(default_factory=dict)
    areas: Dict[str, Area] = field(default_factory=dict)  # New: subobjects/areas

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

    def add_area(self, area: Area):
        if area.name not in self.areas:
            self.areas[area.name] = area

    def get_area(self, area_name: str) -> Optional[Area]:
        return self.areas.get(area_name)

    def move_agent_to_area(self, agent_id: str, area_name: str):
        area = self.get_area(area_name)
        if area:
            # Remove from place-level agents_present if present
            if agent_id in self.agents_present:
                self.agents_present.remove(agent_id)
            area.add_agent(agent_id)
        else:
            raise ValueError(f"Area '{area_name}' not found in place '{self.name}'.")

    def remove_agent_from_area(self, agent_id: str, area_name: str):
        area = self.get_area(area_name)
        if area:
            area.remove_agent(agent_id)
        else:
            raise ValueError(f"Area '{area_name}' not found in place '{self.name}'.")

    def list_areas(self) -> List[str]:
        return list(self.areas.keys())

    # Extend with event handling, metrics, commerce, etc. as needed
