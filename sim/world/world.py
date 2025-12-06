"""
world.py

Defines core world logic for llm-sim, including Vendor class and world-level operations.
Handles item storage, simulation metrics, and world configuration.

Key Classes:
- Vendor: Manages item prices, stock, and buyback logic for places with commerce.

Key Functions:
- fluctuate_prices: Randomly adjust item prices.
- restock: Replenish vendor stock.
- has/take: Check and remove items from stock.

LLM Usage:
- None directly; world logic may be used by agent/world modules that interact with LLMs.

CLI Arguments:
- None directly; world objects are managed by simulation scripts and world configs.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from collections import deque
# Import Inventory for item storage in places
from sim.inventory.inventory import Inventory, ITEMS
from sim.utils.metrics import SimulationMetrics
from dataclasses import dataclass, field
from sim.utils.time_manager import TimeManager
import logging
import yaml

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from sim.agents.agents import Agent
    from sim.agents.persona import Persona

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..agents.agents import Agent


@dataclass
class Vendor:
    prices: Dict[str, float] = field(default_factory=dict)   # item_id -> price
    stock: Dict[str, int] = field(default_factory=dict)      # item_id -> qty
    buyback: Dict[str, float] = field(default_factory=dict)  # item_id -> price

    def fluctuate_prices(self, fluctuation: float = 0.1, min_price: float = 0.01):
        """
        Randomly fluctuate prices for all items by up to ±fluctuation (as a fraction of current price).
        Prices will not drop below min_price.
        """
        import random
        for item_id, price in self.prices.items():
            change = price * random.uniform(-fluctuation, fluctuation)
            new_price = max(min_price, price + change)
            self.prices[item_id] = round(new_price, 2)

    def restock(self, restock_dict: Optional[Dict[str, int]] = None, default_qty: int = 10):
        """
        Replenish vendor stock. If restock_dict is provided, set stock to at least the specified quantity for each item.
        Otherwise, restock all items in prices to at least default_qty.
        """
        if restock_dict:
            for item_id, qty in restock_dict.items():
                current = self.stock.get(item_id, 0)
                if current < qty:
                    self.stock[item_id] = qty
        else:
            for item_id in self.prices:
                current = self.stock.get(item_id, 0)
                if current < default_qty:
                    self.stock[item_id] = default_qty

    def has(self, item_id: str, qty: int = 1) -> bool:
        return self.stock.get(item_id, 0) >= qty

    def take(self, item_id: str, qty: int = 1) -> bool:
        if not self.has(item_id, qty): return False
        self.stock[item_id] -= qty
        return True

    def buy(self, item_id: str, qty: int, agent) -> bool:
        """
        Allow an agent to buy items from the vendor.
        Args:
            item_id (str): ID of the item to buy.
            qty (int): Quantity to buy.
            agent: The agent making the purchase.
        Returns:
            bool: True if the purchase is successful, False otherwise.
        """
        if not self.has(item_id, qty):
            logger.warning(f"Vendor does not have enough stock of item {item_id}.")
            return False

        price = self.prices.get(item_id, 0) * qty
        if not agent.inventory.has("money", price):
            logger.warning(f"Agent {agent.persona.name} does not have enough money to buy {qty} of {item_id}.")
            return False

        # Process the transaction
        agent.inventory.remove("money", price)
        agent.inventory.add(ITEMS[item_id], qty)
        self.take(item_id, qty)
        logger.info(f"Agent {agent.persona.name} bought {qty} of {item_id} for {price} units.")
        return True

    def sell(self, item_id: str, qty: int, agent) -> bool:
        """
        Allow an agent to sell items to the vendor.
        Args:
            item_id (str): ID of the item to sell.
            qty (int): Quantity to sell.
            agent: The agent making the sale.
        Returns:
            bool: True if the sale is successful, False otherwise.
        """
        if not agent.inventory.has(item_id, qty):
            logger.warning(f"Agent {agent.persona.name} does not have enough of item {item_id} to sell.")
            return False

        buyback_price = self.buyback.get(item_id, 0) * qty
        if buyback_price <= 0:
            logger.warning(f"Vendor does not offer buyback for item {item_id}.")
            return False

        # Process the transaction
        agent.inventory.remove(item_id, qty)
        agent.inventory.add(ITEMS["money"], buyback_price)
        self.stock[item_id] = self.stock.get(item_id, 0) + qty
        logger.info(f"Agent {agent.persona.name} sold {qty} of {item_id} for {buyback_price} units.")
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
    areas: Dict[str, Any] = field(default_factory=dict)  # New: subobjects/areas
    attributes: Dict[str, Any] = field(default_factory=dict)  # For initial_area and extensibility

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

    def add_area(self, area: Any):
        """
        Add an area (subobject) to this place.
        """
        if area.name not in self.areas:
            self.areas[area.name] = area

    def get_area(self, area_name: str) -> Optional[Any]:
        """
        Get an area (subobject) by name.
        """
        return self.areas.get(area_name)

    @property
    def agents_present(self):
        """
        Return a list of agents currently in this place.
        """
        return getattr(self, "agents", [])


@dataclass
class World:
    name: str = ""
    time_manager: TimeManager = field(default_factory=lambda: TimeManager(ticks_per_day=144, minutes_per_tick=10))

    def get_time_of_day(self) -> str:
        """
        Return the time of day based on the current tick.
        Example: 'morning', 'afternoon', 'evening', 'night'.
        """
        return self.time_manager.get_time_of_day()

    @property
    def time(self) -> int:
        return self.time_manager.tick

    @time.setter
    def time(self, value: int):
        self.time_manager.set_tick(value)

    @property
    def hour(self) -> int:
        return self.time_manager.hour

    @property
    def minutes(self) -> int:
        return self.time_manager.minutes

    @property
    def day(self) -> int:
        return self.time_manager.day
    def register_event_handlers(self):
        """
        Register subsystem event handlers with the dispatcher.
        """
        if not self.event_dispatcher:
            return
        # Weather event handler: update weather state and notify agents
        def weather_event_handler(event):
            # Accept both {'type': 'weather', 'event': ...} and {'event': ...}
            if self.weather_manager:
                if event.get('type') == 'weather' and 'event' in event:
                    self.weather_manager.current_state = event['event']
                elif 'event' in event:
                    self.weather_manager.current_state = event['event']
            # Affect agent mood for weather events
            for agent in self._agents:
                if hasattr(agent, 'mood') and agent.mood:
                    if event.get('event') == 'rain':
                        agent.mood.update_mood('weather', -0.1)
                    elif event.get('event') == 'sunny':
                        agent.mood.update_mood('weather', 0.1)
        self.event_dispatcher.register_handler('weather', weather_event_handler)

        # Scheduler event handler: update agent schedules and place capabilities
        def scheduler_event_handler(event):
            if event.get('type') == 'festival':
                for agent in self._agents:
                    if hasattr(agent, 'mood') and agent.mood:
                        agent.mood.update_mood('festival', 0.2)
                # Boost activity in all places
                for place in self.places.values():
                    place.purpose = 'festival'
            if event.get('type') == 'store_close':
                place_name = event.get('place')
                if place_name and place_name in self.places:
                    self.places[place_name].capabilities.discard('store')
        self.event_dispatcher.register_handler('festival', scheduler_event_handler)
        self.event_dispatcher.register_handler('store_close', scheduler_event_handler)

        # Accident event handler: update agent physio/mood for affected agents
        def accident_event_handler(event):
            place_name = event.get('place')
            if place_name and place_name in self.places:
                for agent in self.places[place_name].agents_present:
                    if hasattr(agent, 'physio') and agent.physio:
                        agent.physio.stress = min(1.0, agent.physio.stress + 0.3)
                    if hasattr(agent, 'mood') and agent.mood:
                        agent.mood.update_mood('accident', -0.2)
                # Temporarily close the place for accidents
                self.places[place_name].capabilities.discard('open')
        self.event_dispatcher.register_handler('accident', accident_event_handler)

    def dispatch_random_event(self, tick: int):
        """
        Dispatch random and scheduled events to the dispatcher.
        """
        import random
        if not self.event_dispatcher:
            return
        # Random accident event
        if random.random() < 0.01:
            place = random.choice(list(self.places.keys()))
            event = {'type': 'accident', 'place': place, 'tick': tick}
            self.event_dispatcher.dispatch_event(event)
        # Random weather change event (morning)
        if hasattr(self, 'get_time_of_day') and self.get_time_of_day() == 'morning' and random.random() < 0.2:
            weather_event = random.choice(['rain', 'sunny'])
            event = {'type': 'weather', 'event': weather_event, 'tick': tick}
            self.event_dispatcher.dispatch_event(event)
        # Scheduled festival event
        if tick == 100:
            event = {'type': 'festival', 'name': 'Spring Festival', 'tick': tick}
            self.event_dispatcher.dispatch_event(event)
        # Store closing event at night (example)
        if hasattr(self, 'get_time_of_day') and self.get_time_of_day() == 'night':
            for place in self.places.values():
                if 'store' in place.capabilities:
                    event = {'type': 'store_close', 'place': place.name, 'tick': tick}
                    self.event_dispatcher.dispatch_event(event)

    places: Dict[str, Place] = field(default_factory=dict)
    events: deque = field(default_factory=deque)
    _agents: list = field(default_factory=list)  # type: ignore

    agent_locations: dict = field(default_factory=dict)  # Maps agent names to place names
    item_ownership: dict = field(default_factory=dict)  # Maps item IDs to agent/place names
    metrics: SimulationMetrics = field(default_factory=SimulationMetrics)  # Tracks simulation metrics
    weather_manager: Any = None  # Will be set to WeatherManager instance
    event_dispatcher: Any = None  # Will be set to WorldEventDispatcher instance

    def __init__(self, places: Dict[str, Place], name: str = "", events=None, _agents=None, agent_locations=None, item_ownership=None, metrics=None, time_manager=None, sim_logger=None):
        self.name = name
        self.places = places
        self.events = events if events is not None else deque()
        self._agents = _agents if _agents is not None else []
        self.agent_locations = agent_locations if agent_locations is not None else {}
        self.item_ownership = item_ownership if item_ownership is not None else {}
        self.metrics = metrics if metrics is not None else SimulationMetrics()
        self.time_manager = time_manager if time_manager is not None else TimeManager(ticks_per_day=144, minutes_per_tick=10)
        self.sim_logger = sim_logger
        # WeatherManager integration
        try:
            from sim.world.weather import WeatherManager
            self.weather_manager = WeatherManager()
        except ImportError:
            self.weather_manager = None
        # EventDispatcher integration
        try:
            from sim.world.event_dispatcher import WorldEventDispatcher
            self.event_dispatcher = WorldEventDispatcher()
        except ImportError:
            self.event_dispatcher = None
        # Register agent weather hooks if available
        if self.weather_manager:
            for agent in self._agents:
                if hasattr(agent, 'on_weather_update'):
                    self.weather_manager.register_agent_hook(agent.on_weather_update)

    def log_agent_action(self, agent: Agent, action: str):
        """
        Log an agent's action in the simulation metrics.
        Args:
            agent (Agent): The agent performing the action.
            action (str): The action performed.
        """
        self.metrics.log_agent_action(agent.persona.name, action)

    def log_resource_flow(self, entity: str, item_id: str, qty: int):
        """
        Log a resource flow in the simulation metrics.
        Args:
            entity (str): The entity involved in the resource flow (agent or place).
            item_id (str): The ID of the item involved.
            qty (int): The quantity of the item.
        """
        self.metrics.log_resource_flow(entity, item_id, qty)

    def log_world_event(self, event: str):
        """
        Log a world event in the simulation metrics.
        Args:
            event (str): The event to log.
        """
        self.metrics.log_world_event(event)

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
        """
        Run the simulation for a number of ticks using the modular agent scheduler loop.
        Args:
            ticks: Number of simulation ticks to run
        """
        from sim.scheduler.scheduler import run_agent_loop
        self.register_event_handlers()
        for i in range(ticks):
            # Advance world time
            self.time_manager.set_tick(self.time_manager.tick + 1)
            # Set current_tick for centralized time management
            self.current_tick = self.time_manager.tick
            # Update weather each tick
            if self.weather_manager:
                self.weather_manager.update_weather()
            # Dispatch random/scheduled events
            self.dispatch_random_event(self.time_manager.tick)
            # Update metrics tick
            if hasattr(self, 'metrics'):
                self.metrics.set_tick(self.time_manager.tick)
            # Run agent loop for this tick, pass metrics and sim_logger explicitly
            run_agent_loop(self, 1, metrics=self.metrics if hasattr(self, 'metrics') else None, sim_logger=self.sim_logger)
            # Record metrics snapshot for this tick
            if hasattr(self, 'metrics'):
                agent_count = len(self._agents)
                active_events = len(self.events) if hasattr(self, 'events') else 0
                self.metrics.record_tick_snapshot(agent_count=agent_count, active_events=active_events)

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
        from sim.agents.agents import Agent
        from sim.agents.persona import Persona
        
        for agent_data in config.get("agents", []):
            persona = Persona(
                name=agent_data["name"],
                age=agent_data.get("age", 30),
                job=agent_data.get("job", "unemployed"),
                city=agent_data.get("city", "Unknown"),
                bio=agent_data.get("bio", ""),
                values=agent_data.get("values", []),
                goals=agent_data.get("goals", []),
                job_level=agent_data.get("job_level", "entry"),
                job_experience=agent_data.get("job_experience", 0),
                income=agent_data.get("income", 0.0),
                career_history=agent_data.get("career_history", []),
                traits=agent_data.get("traits", {}),
                aspirations=agent_data.get("aspirations", []),
                emotional_modifiers=agent_data.get("emotional_modifiers", {}),
                age_transitions=agent_data.get("age_transitions", {}),
                life_stage=agent_data.get("life_stage", "adult")
            )
            agent = Agent(persona=persona, place=agent_data.get("place", ""))

            # Initialize agent schedule if provided
            if "schedule" in agent_data:
                try:
                    agent.initialize_schedule(agent_data["schedule"])
                except Exception as e:
                    logger.error(f"Failed to initialize schedule for agent {agent.persona.name}: {e}")

            # Ensure the agent's position is valid
            if agent.place not in self.places:
                logger.warning(f"Invalid place '{agent.place}' for agent {agent.persona.name}. Assigning default place.")
                agent.place = next(iter(self.places))  # Assign the first place as default

            # Add agent to the world
            self.add_agent(agent)
            self.set_agent_location(agent, agent.place)

            logger.debug(f"Loaded agent {agent.persona.name} into the world at {agent.place}.")

    def load_places_from_config(self, config: dict):
        """
        Load places from a configuration dictionary.
        Args:
            config (dict): Configuration data containing place details.
        """
        for place_data in config.get("places", []):
            # Parse vendor details if present
            vendor = None
            if "vendor" in place_data:
                vendor_data = place_data["vendor"]
                vendor = Vendor(
                    prices=vendor_data.get("prices", {}),
                    stock=vendor_data.get("stock", {}),
                    buyback=vendor_data.get("buyback", {})
                )

            # Create the Place object
            place = Place(
                name=place_data["name"],
                neighbors=place_data.get("neighbors", []),
                capabilities=set(place_data.get("capabilities", [])),
                vendor=vendor
            )

            # Add the place to the world
            self.places[place.name] = place

            logger.debug(f"Loaded place {place.name} with capabilities {place.capabilities} and neighbors {place.neighbors}.")

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
                if agent.physio and hasattr(agent.physio, 'energy'):
                    agent.physio.energy -= 0.1

                # Ensure the money item exists in ITEMS
                money_item = ITEMS.get("money")
                if money_item and agent.inventory:
                    agent.inventory.add(money_item, reward)
                    logger.info(f"Agent {agent.persona.name} earned {reward} units for working.")
                else:
                    logger.warning("Money item not found in ITEMS or agent inventory missing. Reward not added.")

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
        elif agent.physio and hasattr(agent.physio, 'hunger') and agent.physio.hunger > 0.8:
            decision["action"] = "eat"
            decision["reason"] = "Agent is very hungry."
        else:
            decision["action"] = "explore"
            decision["reason"] = "Default action."

        logger.info(f"Agent {agent.persona.name} decision: {decision}")
        return decision

    def agent_buy(self, agent: Agent, place_name: str, item_id: str, qty: int) -> bool:
        """
        Facilitate an agent buying items from a vendor at a specific place.
        Args:
            agent (Agent): The agent making the purchase.
            place_name (str): The name of the place where the vendor is located.
            item_id (str): The ID of the item to buy.
            qty (int): The quantity to buy.
        Returns:
            bool: True if the transaction is successful, False otherwise.
        """
        if place_name not in self.places:
            logger.error(f"Place '{place_name}' does not exist in the world.")
            return False

        place = self.places[place_name]
        if not place.vendor:
            logger.warning(f"Place '{place_name}' does not have a vendor.")
            return False

        return place.vendor.buy(item_id, qty, agent)

    def agent_sell(self, agent: Agent, place_name: str, item_id: str, qty: int) -> bool:
        """
        Facilitate an agent selling items to a vendor at a specific place.
        Args:
            agent (Agent): The agent making the sale.
            place_name (str): The name of the place where the vendor is located.
            item_id (str): The ID of the item to sell.
            qty (int): The quantity to sell.
        Returns:
            bool: True if the transaction is successful, False otherwise.
        """
        if place_name not in self.places:
            logger.error(f"Place '{place_name}' does not exist in the world.")
            return False

        place = self.places[place_name]
        if not place.vendor:
            logger.warning(f"Place '{place_name}' does not have a vendor.")
            return False

        return place.vendor.sell(item_id, qty, agent)

    def export_metrics(self, filepath: str, format: str = "json") -> bool:
        """
        Export simulation metrics to a file.
        
        Args:
            filepath: Path to the output file
            format: Export format ('json' or 'csv')
        
        Returns:
            True if export succeeded, False otherwise
        """
        if format == "json":
            return self.metrics.export_json(filepath)
        elif format == "csv":
            return self.metrics.export_csv(filepath)
        else:
            logger.error(f"Unknown export format: {format}")
            return False

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current simulation metrics.
        
        Returns:
            Dictionary containing metrics summary
        """
        return self.metrics.summary()

    def serialize_state(self) -> dict:
        """Serialize the entire world state to a dict suitable for YAML export."""
        return {
            "places": {
                name: {
                    "neighbors": place.neighbors,
                    "capabilities": list(place.capabilities),
                    "vendor": {
                        "prices": place.vendor.prices if place.vendor else {},
                        "stock": place.vendor.stock if place.vendor else {},
                        "buyback": place.vendor.buyback if place.vendor else {},
                    } if place.vendor else None,
                    "inventory": place.inventory.serialize() if hasattr(place.inventory, 'serialize') else {},
                    "agents": [agent.persona.name for agent in place.agents],
                    "purpose": place.purpose,
                }
                for name, place in self.places.items()
            },
            "agents": [agent.serialize_state() for agent in self._agents],
            "events": list(self.events),
            "agent_locations": self.agent_locations,
            "item_ownership": self.item_ownership,
            "metrics": self.metrics.serialize() if hasattr(self.metrics, 'serialize') else {},
        }

    def save_state_yaml(self, filepath: str):
        """Save the world state to a YAML file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(self.serialize_state(), f, default_flow_style=False, allow_unicode=True)

    @classmethod
    def load_state_yaml(cls, filepath: str):
        """Load world state from a YAML file and return a World instance."""
        with open(filepath, 'r', encoding='utf-8') as f:
            state = yaml.safe_load(f)
        # Reconstruct places
        places = {}
        for name, pdata in state.get('places', {}).items():
            vendor = None
            if pdata.get('vendor'):
                vendor = Vendor(
                    prices=pdata['vendor'].get('prices', {}),
                    stock=pdata['vendor'].get('stock', {}),
                    buyback=pdata['vendor'].get('buyback', {})
                )
            place = Place(
                name=name,
                neighbors=pdata.get('neighbors', []),
                capabilities=set(pdata.get('capabilities', [])),
                vendor=vendor,
                purpose=pdata.get('purpose', "")
            )
            # Optionally restore inventory if needed
            if 'inventory' in pdata and hasattr(place.inventory, 'load'):
                place.inventory.load(pdata['inventory'])
            places[name] = place
        # Reconstruct agents
        from sim.agents.agents import Agent, Persona
        agents = []
        for agent_data in state.get('agents', []):
            persona_data = agent_data.get("persona", {})
            persona = Persona(
                name=persona_data.get("name", ""),
                age=persona_data.get("age", 0),
                job=persona_data.get("job", "unemployed"),
                city=persona_data.get("city", "Unknown"),
                bio=persona_data.get("bio", ""),
                values=persona_data.get("values", []),
                goals=persona_data.get("goals", []),
                job_level=persona_data.get("job_level", "entry"),
                job_experience=persona_data.get("job_experience", 0),
                income=persona_data.get("income", 0.0),
                career_history=persona_data.get("career_history", []),
                traits=persona_data.get("traits", {}),
                aspirations=persona_data.get("aspirations", []),
                emotional_modifiers=persona_data.get("emotional_modifiers", {}),
                age_transitions=persona_data.get("age_transitions", {}),
                life_stage=persona_data.get("life_stage", "adult"),
                personality=None
            )
            agent = Agent(persona=persona)
            agent.load_state(agent_data)
            agents.append(agent)
        # Create World instance
        world = cls(places=places)
        world._agents = agents
        world.events = deque(state.get('events', []))
        world.agent_locations = state.get('agent_locations', {})
        world.item_ownership = state.get('item_ownership', {})
        # Optionally restore metrics
        if 'metrics' in state and hasattr(world.metrics, 'load'):
            world.metrics.load(state['metrics'])
        return world

