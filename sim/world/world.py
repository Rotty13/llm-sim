from __future__ import annotations
from typing import Dict, List, Optional, Any
from collections import deque
# Import Inventory for item storage in places
from sim.inventory.inventory import Inventory, ITEMS
from dataclasses import dataclass, field

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
    inventory: Inventory = field(default_factory=lambda: Inventory(capacity_weight=100.0))  # Item storage for the place

    def get_items(self) -> dict:
        """Return a dict of item_id to quantity for all items stored in this place."""
        return {s.item.id: s.qty for s in self.inventory.stacks}

    def add_agent(self, agent: Any):
        """
        Add an agent to this place.
        """
        if not hasattr(self, "agents"):
            self.agents = []
        self.agents.append(agent)

    @property
    def agents_present(self):
        """
        Return a list of agents currently in this place.
        """
        return getattr(self, "agents", [])

@dataclass
class World:
    places: Dict[str, Place]
    events: deque = field(default_factory=deque)
    _agents: list = field(default_factory=list)  # type: ignore

    agent_locations: dict = field(default_factory=dict)  # Maps agent names to place names
    item_ownership: dict = field(default_factory=dict)  # Maps item IDs to agent/place names

    def set_agent_location(self, agent: Any, place_name: str):
        """Set the location of an agent in the world."""
        if place_name not in self.places:
            raise ValueError(f"Place '{place_name}' does not exist in the world.")
        self.agent_locations[agent.persona.name] = place_name

    def get_agent_location(self, agent_name: str) -> Optional[str]:
        """Get the location of an agent by name."""
        return self.agent_locations.get(agent_name)

    def transfer_item(self, agent, place, item_id, qty):
        """
        Transfer an item from an agent to a place.
        """
        if agent.inventory.has(item_id, qty):
            agent.inventory.remove(item_id, qty)
            place.inventory.add(ITEMS[item_id], qty)
            return True
        return False

    def get_item_owner(self, item_id: str) -> Optional[str]:
        """Get the owner of an item by ID."""
        return self.item_ownership.get(item_id)

    def simulation_loop(self, ticks: int = 100):
        """Run the simulation for a number of ticks."""
        from sim.scheduler.scheduler import enforce_schedule
        for tick in range(ticks):
            for agent in self._agents:
                # Pass busy_until to enforce_schedule
                forced_move = enforce_schedule(agent.calendar, agent.place, tick, agent.busy_until)
                if forced_move:
                    import json
                    payload = json.loads(forced_move[forced_move.find("(")+1:forced_move.rfind(")")])
                    dest = payload.get("to")
                    if dest:
                        agent.move_to(self, dest)
                if hasattr(agent, 'step_interact'):
                    agent.step_interact(self, [a for a in self._agents if a != agent], '', tick, None, None)

    def get_all_places(self) -> list:
        """Return a list of all place names in the world."""
        return list(self.places.keys())

    def get_all_agents(self) -> list:
        """Return a list of all agents in the world."""
        return self._agents

    def get_all_items(self) -> set:
        """Return a set of all item IDs present in all places and agents."""
        item_ids = set()
        for place in self.places.values():
            item_ids.update({s.item.id for s in place.inventory.stacks})
        for agent in self._agents:
            if hasattr(agent, 'get_owned_items'):
                item_ids.update(agent.get_owned_items().keys())
        return item_ids

    def add_agent(self, agent: Any):
        """Add an agent to the world."""
        if agent not in self._agents:
            self._agents.append(agent)

    def remove_agent(self, agent: Any):
        """Remove an agent from the world."""
        if agent in self._agents:
            self._agents.remove(agent)

    def broadcast(self, place_name: str, message: dict):
        """
        Broadcast a message to all agents in a specific place.
        Args:
            place_name (str): The name of the place where the message is broadcast.
            message (dict): The message to broadcast.
        """
        if place_name in self.places:
            for agent in self._agents:
                if self.get_agent_location(agent.persona.name) == place_name:
                    agent.add_observation(message)

    def valid_place(self, place_name: str) -> bool:
        """
        Check if a place name is valid (exists in the world).
        Args:
            place_name (str): The name of the place to check.
        Returns:
            bool: True if the place exists, False otherwise.
        """
        return place_name in self.places

