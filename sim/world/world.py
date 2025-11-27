from __future__ import annotations
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from collections import deque
# Import Inventory for item storage in places
from sim.inventory.inventory import Inventory, ITEMS
from dataclasses import dataclass, field
import logging

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from sim.agents.agents import Agent, Persona

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    agents: List[Any] = field(default_factory=list)  # List of agents currently in the place

    def get_items(self) -> dict:
        """Return a dict of item_id to quantity for all items stored in this place."""
        return {s.item.id: s.qty for s in self.inventory.stacks}

    def add_agent(self, agent: Any):
        """
        Add an agent to this place.
        """
        if not hasattr(self, "agents"):
            self.agents = []
        # Debugging: Log agent addition
        print(f"Adding agent {agent} to place {self.name}.")

        # Prevent duplicate entries
        if agent in self.agents:
            print(f"Agent {agent} is already in place {self.name}. Skipping addition.")
            return

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

        # Remove agent from current place
        current_place_name = self.get_agent_location(agent.persona.name)
        if current_place_name and current_place_name in self.places:
            current_place = self.places[current_place_name]
            if hasattr(current_place, 'agents_present') and agent in current_place.agents_present:
                current_place.agents.remove(agent)

        # Debugging: Log agent movement
        logger.debug(f"Moving agent {agent.persona.name} from {current_place_name} to {place_name}.")
        if current_place_name and current_place_name in self.places:
            logger.debug(f"Agents in {current_place_name} before removal: {current_place.agents_present}")
        logger.debug(f"Agents in {place_name} before addition: {self.places[place_name].agents_present}")

        # Debugging: Print agent movement
        print(f"Moving agent {agent.persona.name} from {current_place_name} to {place_name}.")
        if current_place_name and current_place_name in self.places:
            print(f"Agents in {current_place_name} before removal: {current_place.agents_present}")
        print(f"Agents in {place_name} before addition: {self.places[place_name].agents_present}")

        # Add agent to the new place
        self.places[place_name].add_agent(agent)
        self.agent_locations[agent.persona.name] = place_name

        # Remove all occurrences of the agent from the previous location
        if current_place_name and current_place_name in self.places:
            current_place = self.places[current_place_name]
            while agent in current_place.agents:
                current_place.agents.remove(agent)

        # Debugging: Confirm removal
        if current_place_name and agent in current_place.agents_present:
            print(f"Failed to remove agent {agent.persona.name} from {current_place_name}.")
        elif current_place_name:
            print(f"Successfully removed agent {agent.persona.name} from {current_place_name}.")

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
        events = []  # Placeholder for tick-based events

        for tick in range(ticks):
            print(f"Tick {tick}: Simulation running...")  # Debugging output

            # Process scheduled events for the current tick
            for event in [e for e in events if e['tick'] == tick]:
                event['action'](self)

            for agent in self._agents:
                # Enforce schedules dynamically
                forced_move = enforce_schedule(agent.calendar, agent.place, tick, agent.busy_until)
                # Ensure enforce_schedule handles overlapping appointments
                if forced_move:
                    try:
                        import json
                        payload = json.loads(forced_move[forced_move.find("(")+1:forced_move.rfind(")")])
                        dest = payload.get("to")
                        if dest:
                            agent.move_to(self, dest)
                    except (json.JSONDecodeError, AttributeError) as e:
                        print(f"Error processing schedule for agent {agent.persona.name}: {e}")

                # Allow agents to interact with the world
                if hasattr(agent, 'step_interact'):
                    agent.step_interact(self, [a for a in self._agents if a != agent], '', tick, None, None)

            # Example: Add dynamic events (e.g., world events)
            if tick % 10 == 0:  # Example condition for adding an event
                events.append({
                    'tick': tick + 5,
                    'action': lambda world: print(f"Dynamic event triggered at tick {tick + 5}")
                })

            # Debugging: Print agent locations
            for agent in self._agents:
                location = self.get_agent_location(agent.persona.name)
                print(f"Agent {agent.persona.name} is at {location}")

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

    def load_agents_from_config(self, config: dict):
        """
        Load agents from a configuration dictionary.
        Args:
            config (dict): Configuration data containing agent details.
        """
        # Lazy import to avoid circular dependency
        from sim.agents.agents import Agent, Persona
        
        for agent_data in config.get("agents", []):
            persona = Persona(
                name=agent_data["name"],
                age=agent_data.get("age", 30),
                job=agent_data.get("job", "unemployed"),
                city=agent_data.get("city", "Unknown"),
                bio=agent_data.get("bio", ""),
                values=agent_data.get("values", []),
                goals=agent_data.get("goals", [])
            )
            agent = Agent(persona=persona, place=agent_data.get("place", ""))

            # Initialize agent schedule if provided
            if "schedule" in agent_data:
                agent.initialize_schedule(agent_data["schedule"])

            # Add agent to the world
            self.add_agent(agent)
            self.set_agent_location(agent, agent.place)

            logger.debug(f"Loaded agent {agent.persona.name} into the world at {agent.place}.")

    def validate_agent_positions(self):
        """
        Ensure all agents are placed in valid locations.
        """
        for agent in self._agents:
            if agent.place not in self.places:
                logger.warning(f"Agent {agent.persona.name} is in an invalid place: {agent.place}. Moving to default place.")
                default_place = next(iter(self.places))  # Pick the first place as default
                self.set_agent_location(agent, default_place)
                logger.info(f"Agent {agent.persona.name} moved to default place: {default_place}.")

    def implement_work_action(self, agent: 'Agent'):
        """
        Implement the WORK action for an agent, with job-site validation and prerequisites.
        """
        if agent.place in self.places:
            place = self.places[agent.place]

            # Check if the place has the capability for work
            if "work" in place.capabilities:
                logger.info(f"Agent {agent.persona.name} is working at {agent.place}.")

                # Ensure the place has a vendor and a reward price
                if place.vendor and "work_reward" in place.vendor.prices:
                    reward = int(place.vendor.prices["work_reward"])
                else:
                    reward = 10  # Default reward if not defined

                # Simulate work by reducing agent's energy and adding a reward
                agent.physio.energy -= 0.1

                # Ensure the money item exists in ITEMS
                money_item = ITEMS.get("money")
                if money_item:
                    agent.inventory.add(money_item, reward)
                    logger.info(f"Agent {agent.persona.name} earned {reward} units for working.")
                else:
                    logger.warning("Money item not found in ITEMS. Reward not added.")

                return True

            else:
                logger.warning(f"Agent {agent.persona.name} cannot work at {agent.place} as it lacks work capability.")
        else:
            logger.error(f"Agent {agent.persona.name} is not in a valid place to work.")

        return False

    def consolidate_decision_logic(self, agent: 'Agent', context: dict):
        """
        Consolidate decision logic for agents.
        """
        decision = {}
        if agent.persona.values and "kindness" in agent.persona.values:
            decision["action"] = "help"
            decision["reason"] = "Agent values kindness."
        elif agent.physio.hunger > 0.8:
            decision["action"] = "eat"
            decision["reason"] = "Agent is very hungry."
        else:
            decision["action"] = "explore"
            decision["reason"] = "Default action."

        logger.info(f"Agent {agent.persona.name} decision: {decision}")
        return decision

