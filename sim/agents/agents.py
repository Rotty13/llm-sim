from __future__ import annotations

"""
agents.py


Defines agent classes and data structures for llm-sim simulation.
Contains Persona, Physio, and Agent dataclasses for modeling agent behavior,
physiological state, and decision-making.

Key Classes:
- Persona: Represents an agent's identity, job, values, goals, and personality traits.
- Physio: Represents an agent's physiological state (hunger, energy, stress, mood, etc.).
- Agent: Main agent class with decision-making, memory, inventory, and movement capabilities.

Modular Delegation:
- Agent delegates physiological state and moodlet management to AgentPhysio (sim.agents.modules.agent_physio).
- Agent delegates plan logic and per-tick planning to AgentPlanLogic (sim.agents.modules.agent_plan_logic).
- Action execution is delegated to AgentActions (sim.agents.modules.agent_actions).
- Inventory management is delegated to AgentInventory (sim.agents.modules.agent_inventory).
- Other concerns (memory, social, serialization, relationships) are handled by respective modules.
  
**Any extension of agent functionality—including life stage logic, behavioral modifiers, new capabilities, or decision logic—should be delegated to appropriate modules (e.g., AgentPhysio, AgentPlanLogic, AgentActions, AgentInventory, AgentMemory, etc.) whenever possible. This ensures modularity, maintainability, and clarity.**

Key Constants:
- JOB_SITE: Dictionary mapping job names to expected work locations.

LLM Usage:
- Uses sim.llm.llm_ollama for conversation and decision-making with LLM.

CLI Arguments:
- None directly; agents are managed by simulation scripts and world modules.

Recent Refactor Notes:
- Agent class logic for moodlets and physiological updates is now delegated to AgentPhysio.
- Plan logic and per-tick updates are delegated to AgentPlanLogic.
- Inventory logic is now delegated to AgentInventory.
- Agent class is slimmer and more modular, focusing on orchestration and high-level decision-making.
"""

import json
import random
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, TYPE_CHECKING

# YAML loading utility
import yaml

def load_yaml_config(path: str) -> dict:
    """Load a YAML config file and return as dict."""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

from sim.inventory.inventory import Inventory, Item, ITEMS
from sim.memory.memory import MemoryItem, MemoryStore
from sim.scheduler.scheduler import Appointment, enforce_schedule
from sim.utils.utils import now_str
from sim.agents.controllers import LogicController
from sim.agents.physio import Physio
from sim.agents.persona import Persona
from sim.agents.modules.agent_mood import AgentMood
from sim.agents.modules.agent_inventory import AgentInventory
from sim.agents.modules.agent_memory import AgentMemory
from sim.agents.modules.agent_actions import AgentActions
from sim.agents.modules.agent_social import AgentSocial
from sim.agents.modules.agent_serialization import AgentSerialization
from sim.agents.modules.agent_relationships import AgentRelationships
from sim.agents.memory_manager import MemoryManager
from sim.agents.inventory_handler import InventoryHandler
from sim.agents.decision_controller import DecisionController
from sim.agents.movement_controller import MovementController
from sim.agents.interaction import preference_to_interact
from sim.actions.actions import parse_action
from sim.llm.llm_ollama import LLM
# Create a module-level LLM instance for conversation
llm = LLM()

# Import centralized simulation constants
from sim.utils.constants import JOB_SITE



@dataclass
class Agent:
    # =============================
    # Initialization & Config Loading
    # =============================
    @classmethod
    def from_yaml(
        cls,
        agent_path: str,
        persona_path: str,
        physio_path: str,
        modules_config: Optional[dict] = None,
        decisionrules_path: Optional[str] = None,
        physio_rules_path: Optional[str] = None,
        inventory_rules_path: Optional[str] = None,
        social_rules_path: Optional[str] = None,
        schedule_rules_path: Optional[str] = None
    ):
        """
        Factory method to create Agent from YAML config files.
        Args:
            agent_path: Path to agent YAML config
            persona_path: Path to persona YAML config
            physio_path: Path to physio YAML config
            modules_config: Optional dict to override module enable/disable
            rules_path: Optional path to agent decision/action rules YAML config
            physio_rules_path: Optional path to physio/mood rules YAML config
            inventory_rules_path: Optional path to inventory rules YAML config
            social_rules_path: Optional path to social/relationship rules YAML config
            schedule_rules_path: Optional path to schedule rules YAML config
        """
        agent_cfg = load_yaml_config(agent_path)
        persona_cfg = load_yaml_config(persona_path)
        physio_cfg = load_yaml_config(physio_path)

        # Create Persona and Physio objects from config
        persona = Persona(**persona_cfg['persona'])
        physio = Physio(**physio_cfg['physio'])

        # Compose Agent fields from config
        modules = agent_cfg.get('modules', {})
        if modules_config:
            modules.update(modules_config)

        # Calendar (schedule)
        calendar = []
        for entry in agent_cfg.get('calendar', []):
            if isinstance(entry, dict):
                calendar.append(Appointment(
                    start_tick=entry.get('start_tick', 0),
                    end_tick=entry.get('end_tick', 0),
                    location=entry.get('location', ''),
                    label=entry.get('label', '')
                ))

        # Traits
        traits = agent_cfg.get('traits', persona_cfg.get('traits', []))
        persona.traits = traits

        # Place
        place = agent_cfg.get('place', 'Home')

        # Build config dict for module enable/disable
        config = modules

        # Load decision/action rules from YAML if provided
        decision_rules = load_yaml_config(decisionrules_path) if decisionrules_path else None
        physio_rules = load_yaml_config(physio_rules_path) if physio_rules_path else None
        inventory_rules = load_yaml_config(inventory_rules_path) if inventory_rules_path else None
        social_rules = load_yaml_config(social_rules_path) if social_rules_path else None
        schedule_rules = load_yaml_config(schedule_rules_path) if schedule_rules_path else None

        # Instantiate Agent
        return cls(
            persona=persona,
            physio=physio,
            place=place,
            config=config,
            calendar=calendar,
            rules=decision_rules,
            physio_rules=physio_rules,
            inventory_rules=inventory_rules,
            social_rules=social_rules,
            schedule_rules=schedule_rules
        )
    def get_recent_conversation_topics(self, limit=10, agent_name=None):
        """Return recent conversation topics from AgentSocial."""
        if self.social:
            return self.social.get_recent_topics(agent_name or self.persona.name, limit)
        return []

    def on_weather_update(self, weather_state: str):
        """
        Respond to weather updates. Delegates logic to appropriate modules if available.
        """
        # Example: delegate to physio, mood, or plan logic modules
        if hasattr(self, 'physio') and self.physio:
            if hasattr(self.physio, 'on_weather_update'):
                self.physio.on_weather_update(weather_state)
        if hasattr(self, 'mood') and self.mood:
            if hasattr(self.mood, 'on_weather_update'):
                self.mood.on_weather_update(weather_state)
        # Add more delegation as needed
        # Placeholder: print for debug
        print(f"Agent {self.persona.name} received weather update: {weather_state}")
    def update_affinity(self, other: str, delta: float):
        if self.social:
            self.social.update_affinity(other, delta)

    def update_rivalry(self, other: str, delta: float):
        if self.social:
            self.social.update_rivalry(other, delta)

    def update_influence(self, other: str, delta: float):
        if self.social:
            self.social.update_influence(other, delta)
    # General interaction methods
    def work_at_place(self, place: Any, world: Any, tick: int) -> bool:
        """Delegate work action to AgentActions."""
        if self.actions:
            return self.actions.work_at_place(self, place, world, tick)
        return False

    def buy_from_vendor(self, vendor: Any, item_id: str, qty: int = 1) -> bool:
        """Delegate buy action to AgentActions."""
        if self.actions:
            return self.actions.buy_from_vendor(self, vendor, item_id, qty)
        return False

    def sell_to_vendor(self, vendor: Any, item_id: str, qty: int = 1) -> bool:
        """Delegate sell action to AgentActions."""
        if self.actions:
            return self.actions.sell_to_vendor(self, vendor, item_id, qty)
        return False

    def interact_with_inventory(self, inventory: Any, item_id: str, qty: int = 1) -> bool:
        """Delegate inventory interaction to AgentActions."""
        if self.actions:
            return self.actions.interact_with_inventory(self, inventory, item_id, qty)
        return False

    def interact_with_place(self, place: Any, item_id: str, qty: int = 1) -> bool:
        """Delegate place interaction to AgentActions."""
        if self.actions:
            return self.actions.interact_with_place(self, place, item_id, qty)
        return False
    # Required fields (no defaults - must be provided)
    persona: Persona
    place: str = "Home"
    config: Optional[Dict[str, bool]] = None
    calendar: List[Appointment] = field(default_factory=list)
    controller: Any = field(default_factory=LogicController)
    mood: Optional[AgentMood] = field(default_factory=AgentMood)
    physio: Optional[Physio] = field(default_factory=Physio)
    inventory: Optional[AgentInventory] = field(default_factory=AgentInventory)
    memory: Optional[AgentMemory] = field(default_factory=AgentMemory)
    actions: Optional[AgentActions] = field(default_factory=AgentActions)
    social: Optional[AgentSocial] = field(default_factory=AgentSocial)
    serialization: Optional[AgentSerialization] = field(default_factory=AgentSerialization)
    relationships: Optional[AgentRelationships] = field(default_factory=AgentRelationships)
    plan: List[str] = field(default_factory=list)
    obs_list: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_manager: Optional[MemoryManager] = field(default_factory=MemoryManager)
    inventory_handler: Optional[InventoryHandler] = field(default_factory=InventoryHandler)
    decision_controller: Optional[DecisionController] = field(default_factory=DecisionController)
    movement_controller: Optional[MovementController] = field(default_factory=MovementController)
    busy_until: int = 0
    alive: bool = True
    time_of_death: Optional[int] = None
    social_memory: List[Dict[str, Any]] = field(default_factory=list)
    # Runtime fields (not serialized)
    _last_say_tick: int = field(default=-999, repr=False)
    _last_diary_tick: int = field(default=-999, repr=False)
    _last_diary: str = field(default="", repr=False)
    # New fields for externalized rules/configs
    rules: Optional[dict] = None
    physio_rules: Optional[dict] = None
    inventory_rules: Optional[dict] = None
    social_rules: Optional[dict] = None
    schedule_rules: Optional[dict] = None
    # Utility methods to access loaded rules/configs
    def get_physio_rules(self):
        """Return loaded physio/mood rules from YAML."""
        if self.physio_rules:
            return self.physio_rules
        return {}

    def get_inventory_rules(self):
        """Return loaded inventory rules from YAML."""
        if self.inventory_rules:
            return self.inventory_rules
        return {}

    def get_social_rules(self):
        """Return loaded social/relationship rules from YAML."""
        if self.social_rules:
            return self.social_rules
        return {}

    def get_schedule_rules(self):
        """Return loaded schedule rules from YAML."""
        if self.schedule_rules:
            return self.schedule_rules
        return {}
    def get_decision_rules(self):
        """Return loaded decision rules from YAML."""
        if self.rules and 'decision_rules' in self.rules:
            return self.rules['decision_rules']
        return []

    def get_action_rules(self):
        """Return loaded action rules from YAML."""
        if self.rules and 'action_rules' in self.rules:
            return self.rules['action_rules']
        return []

    def assign_job(self, job: str, job_level: str = "entry", income: float = 0.0):
        """Assign a new job to the agent, updating career history and resetting experience."""
        if self.persona.job:
            self.persona.career_history.append(self.persona.job)
        self.persona.job = job
        self.persona.job_level = job_level
        self.persona.job_experience = 0
        self.persona.income = income

    def promote(self, new_level: str, income_increase: float = 0.0):
        """Promote agent to a new job level and optionally increase income."""
        self.persona.job_level = new_level
        if income_increase:
            self.persona.income += income_increase

    def increment_job_experience(self, amount: int = 1):
        """Increment job experience by amount (default 1)."""
        self.persona.job_experience += amount

    def update_income(self):
        """Add current income to agent's money balance."""
        self.receive_income(int(self.persona.income))
    config: Optional[Dict[str, bool]] = None
    calendar: List[Appointment] = field(default_factory=list)
    controller: Any = field(default_factory=LogicController)
    mood: Optional[AgentMood] = field(default_factory=AgentMood)
    physio: Optional[Physio] = field(default_factory=Physio)
    inventory: Optional[AgentInventory] = field(default_factory=AgentInventory)
    memory: Optional[AgentMemory] = field(default_factory=AgentMemory)
    actions: Optional[AgentActions] = field(default_factory=AgentActions)
    social: Optional[AgentSocial] = field(default_factory=AgentSocial)
    serialization: Optional[AgentSerialization] = field(default_factory=AgentSerialization)
    relationships: Optional[AgentRelationships] = field(default_factory=AgentRelationships)
    plan: List[str] = field(default_factory=list)
    obs_list: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_manager: Optional[MemoryManager] = field(default_factory=MemoryManager)
    inventory_handler: Optional[InventoryHandler] = field(default_factory=InventoryHandler)
    decision_controller: Optional[DecisionController] = field(default_factory=DecisionController)
    movement_controller: Optional[MovementController] = field(default_factory=MovementController)
    busy_until: int = 0
    alive: bool = True
    time_of_death: Optional[int] = None
    social_memory: List[Dict[str, Any]] = field(default_factory=list)
    # Runtime fields (not serialized)
    _last_say_tick: int = field(default=-999, repr=False)
    _last_diary_tick: int = field(default=-999, repr=False)
    _last_diary: str = field(default="", repr=False)

    def die(self, tick: int):
        """Mark the agent as dead and record time of death."""
        self.alive = False
        self.time_of_death = tick

    def update_life_stage(self):
            """Update life stage based on age using config-driven transitions."""
            age = getattr(self.persona, 'age', None)
            transitions = getattr(self.persona, 'age_transitions', None)
            if age is not None and transitions:
                # transitions: {infant: 0, toddler: 3, child: 6, teen: 13, young_adult: 20, adult: 36, elder: 65}
                stages = sorted(transitions.items(), key=lambda x: x[1])
                for i, (stage, min_age) in enumerate(stages):
                    next_min_age = stages[i+1][1] if i+1 < len(stages) else float('inf')
                    if age >= min_age and age < next_min_age:
                        self.persona.life_stage = stage
                        break

    @property
    def money_balance(self):
        """Return the agent's money balance from inventory (delegated)."""
        if self.inventory:
            return self.inventory.get_quantity("money")
        return 0

    def receive_income(self, amount: int):
        """Add income to agent's money balance (delegated)."""
        if self.inventory:
            self.inventory.add_item("money", amount)


    def __post_init__(self):
        # If config is provided, enable/disable modules accordingly
        if self.config:
            module_map = {
                'mood': AgentMood,
                'physio': Physio,
                'inventory': AgentInventory,
                'memory': AgentMemory,
                'actions': AgentActions,
                'social': AgentSocial,
                'serialization': AgentSerialization,
                'relationships': AgentRelationships,
                'memory_manager': MemoryManager,
                'inventory_handler': InventoryHandler,
                'decision_controller': DecisionController,
                'movement_controller': MovementController,
            }
            for key, module_cls in module_map.items():
                enabled = self.config.get(key, True)
                setattr(self, key, module_cls() if enabled else None)
        # Add references to new modules for delegation
        from sim.agents.modules.agent_physio import AgentPhysio
        self.agent_physio = AgentPhysio(self.physio)
        from sim.agents.modules.agent_observation import AgentObservation
        self.agent_observation = AgentObservation(self.memory_manager)
        from sim.agents.modules.agent_inventory_place import AgentInventoryPlace
        self.agent_inventory_place = AgentInventoryPlace(self.inventory)
        from sim.agents.modules.agent_llm import AgentLLM
        self.agent_llm = AgentLLM(self)
        from sim.agents.modules.agent_schedule import AgentSchedule
        self.agent_schedule = AgentSchedule(self)
        from sim.agents.modules.agent_stubs import AgentStubs
        self.agent_stubs = AgentStubs()
        from sim.agents.modules.agent_plan_logic import AgentPlanLogic
        self.agent_plan_logic = AgentPlanLogic()


    def check_death_conditions(self, tick: int, world: Any = None):
            """Check if agent meets any death conditions and trigger death if so (config-driven)."""
            # Get death thresholds from physio config
            thresholds = getattr(self.physio, 'death_thresholds', {})
            max_age = thresholds.get('max_age', 100)
            min_hunger = thresholds.get('min_hunger', 0)
            min_energy = thresholds.get('min_energy', 0)
            max_stress = thresholds.get('max_stress', 1)
            min_bladder = thresholds.get('min_bladder', 0)
            age = getattr(self.persona, 'age', None)
            if age is not None and age >= max_age:
                self.die(tick)
                return 'old_age'
            if self.agent_physio and self.agent_physio.physio:
                physio = self.agent_physio.physio
                if getattr(physio, 'hunger', 1) <= min_hunger:
                    self.die(tick)
                    return 'starvation'
                if getattr(physio, 'energy', 1) <= min_energy:
                    self.die(tick)
                    return 'exhaustion'
                if getattr(physio, 'stress', 0) >= max_stress:
                    self.die(tick)
                    return 'stress'
                if getattr(physio, 'bladder', 1) <= min_bladder:
                    self.die(tick)
                    return 'bladder_failure'
            # External event stub (for future expansion)
            # if world and hasattr(world, 'external_death_event'):
            #     if world.external_death_event(self):
            #         self.die(tick)
            #         return 'external_event'
            return None

    def get_relationship(self, other: str) -> Dict[str, float]:
        if self.relationships:
            return self.relationships.get_relationship(other)
        return {}


    def update_familiarity(self, other: str, delta: float):
        if self.relationships:
            self.relationships.update_familiarity(other, delta)


    def update_trust(self, other: str, delta: float):
        if self.relationships:
            self.relationships.update_trust(other, delta)


    # ...existing code...

    def tick_update(self, world: Any, tick: int):
        """
        Update agent state each tick by delegating to modules, including per-tick plan update.
        Also checks for death conditions and triggers death if needed.
        """
        if not self.alive:
            return
        # Check death conditions BEFORE updating physio, so agents with critical needs die immediately
        death_reason = self.check_death_conditions(tick, world)
        if not self.alive:
            return
        if self.agent_physio:
            self.agent_physio.update_tick(self, world, tick)
        # Check death conditions again in case needs changed during update
        death_reason = self.check_death_conditions(tick, world)
        if self.alive:
            # Restore per-tick plan update
            from sim.agents.modules.agent_plan_logic import AgentPlanLogic
            AgentPlanLogic.update_plan(self)
        # Career progression: increment experience and pay income if agent has a job
        if self.persona.job:
            self.increment_job_experience()
            self.update_income()

    def perform_action(self, decision: Dict[str, Any], world: Any, tick: int, **kwargs):
        """
        Perform the given action in the simulation context by delegating to AgentActions.
        Args:
            decision: Decision dictionary (e.g., {'action': 'MOVE', ...})
            world: The simulation world object
            tick: Current simulation tick
        """
        if self.actions:
            self.actions.execute(self, world, decision, tick, **kwargs)

    def serialize_state(self) -> dict:
        """Serialize agent state for saving."""
        physio_state = {}
        if self.agent_physio and self.agent_physio.physio:
            physio = self.agent_physio.physio
            physio_state = {
                "hunger": getattr(physio, "hunger", None),
                "energy": getattr(physio, "energy", None),
                "stress": getattr(physio, "stress", None),
                "mood": getattr(physio, "mood", None),
                "social": getattr(physio, "social", None),
                "fun": getattr(physio, "fun", None),
                "hygiene": getattr(physio, "hygiene", None),
                "comfort": getattr(physio, "comfort", None),
                "bladder": getattr(physio, "bladder", None),
            }
        inventory_state = {}
        if self.inventory:
            inventory_state = self.inventory.serialize()
        memory_state = {}
        if self.memory:
            memory_state = self.memory.serialize()
        plan_state = self.plan.copy() if self.plan else []
        # Serialize relationships as a plain dict
        relationships_state = {}
        if self.relationships and hasattr(self.relationships, 'serialize'):
            relationships_state = self.relationships.serialize()
        elif self.relationships and hasattr(self.relationships, '__dict__'):
            relationships_state = dict(self.relationships.__dict__)
        else:
            relationships_state = {}
        return {
            "persona": {
                "name": self.persona.name,
                "age": self.persona.age,
                "job": self.persona.job,
                "job_level": self.persona.job_level,
                "job_experience": self.persona.job_experience,
                "income": self.persona.income,
                "career_history": self.persona.career_history,
                "city": self.persona.city,
                "bio": self.persona.bio,
                "values": self.persona.values,
                "goals": self.persona.goals,
                "traits": self.persona.traits,
                "aspirations": self.persona.aspirations,
                "emotional_modifiers": self.persona.emotional_modifiers,
                "age_transitions": self.persona.age_transitions,
                "life_stage": self.persona.life_stage,
            },
            "place": self.place,
            "physio": physio_state,
            "inventory": inventory_state,
            "memory": memory_state,
            "plan": plan_state,
            "alive": self.alive,
            "time_of_death": self.time_of_death,
            "relationships": relationships_state,
        }

    def load_state(self, state: dict):
        """Load agent state from saved data."""
        if "place" in state:
            self.place = state["place"]
        if "alive" in state:
            self.alive = state["alive"]
        if "time_of_death" in state:
            self.time_of_death = state["time_of_death"]
        if "relationships" in state:
            self.relationships = state["relationships"]
        if "physio" in state and self.agent_physio and self.agent_physio.physio:
            physio = self.agent_physio.physio
            for key, value in state["physio"].items():
                if hasattr(physio, key):
                    setattr(physio, key, value)
        if "inventory" in state and self.inventory:
            self.inventory.load(state["inventory"])
        if "memory" in state and self.memory:
            self.memory.load(state["memory"])
        if "plan" in state:
            self.plan = state["plan"]
        # ...existing code...

    # Inventory logic delegated to AgentInventory
    def add_money(self, amount: int):
        """Add money to the agent's inventory (delegated)."""
        if self.inventory:
            self.inventory.add_item("money", amount)

    def remove_money(self, amount: int) -> bool:
        """Remove money from the agent's inventory (delegated). Returns True if successful."""
        if self.inventory:
            return self.inventory.remove("money", amount)
        return False

    def step_interact(
        self, world: Any, participants: list, obs: str, tick: int,
        start_dt: Optional[datetime], incoming_message: Optional[dict],
        loglist: Optional[list] = None
    ):
        """
        Delegate step_interact logic to AgentPlanLogic module.
        """
        if self.agent_plan_logic:
            return self.agent_plan_logic.step_interact(self, world, participants, obs, tick, start_dt, incoming_message, loglist)
        return None

    def decide_conversation(
        self, participants: List[Any], obs: str, tick: int,
        incoming_message: Optional[dict], start_dt: Optional[datetime] = None,
        loglist: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Delegate conversation decision logic to AgentLLM module.
        """
        if self.agent_llm:
            result = self.agent_llm.decide_conversation(self, participants, obs, tick, incoming_message, start_dt, loglist)
            # Topic extraction: try 'topic' in result, else from incoming_message
            topic = None
            if isinstance(result, dict):
                topic = result.get('topic')
            if not topic and isinstance(incoming_message, dict):
                topic = incoming_message.get('topic')
            # Log topic in AgentSocial
            if topic and self.social:
                # Log interaction with all participants except self
                for p in participants:
                    if p != self:
                        self.social.log_interaction(p.persona.name, 'conversation', topic)
            return result
        return {}

    # ...existing code...

    def _work_allowed_here(self, world: Any) -> bool:
        """Check if the agent's job allows working at the current location."""
        expected = JOB_SITE.get(self.persona.job)
        return bool(expected) and self.place == expected

    def _eat_allowed_here(self, world: Any) -> bool:
        """Check if eating is allowed at the current location."""
        if not hasattr(world, 'places') or self.place not in world.places:
            return False
        p = world.places[self.place]
        return "food" in p.capabilities or "food_home" in p.capabilities

    def decide(self, world: Any, obs_text: str, tick: int, start_dt: Optional[datetime]) -> Dict[str, Any]:
        """
        Delegate decision-making logic to AgentPlanLogic module.
        Relationship effects can be integrated here for future expansion.
        """
        # Example: use affinity/rivalry/influence in decision logic
        # relationships = self.relationships
        # TODO: Integrate relationship effects into decision-making
        if self.agent_plan_logic:
            return self.agent_plan_logic.decide(self, world, obs_text, tick, start_dt)
        return {"action": "THINK", "private_thought": "I have nothing to do right now."}

    def enforce_schedule(self, tick: int):
        """
        Integrates the `busy_until` attribute with the scheduler to enforce appointments and schedules.
        """
        if self.busy_until > tick:
            return  # Agent is busy

        for appointment in self.calendar:
            if appointment.start_tick == tick:
                self.place = appointment.location
                self.busy_until = appointment.end_tick
                break

    def update_item_ownership(self, world: Any):
        """
        Updates item ownership using the world's `item_ownership` dictionary.
        Records which items this agent owns.
        """
        if not hasattr(world, 'item_ownership'):
            return
        if self.inventory and hasattr(self.inventory, 'all_items'):
            for item, qty in self.inventory.all_items().items():
                world.item_ownership[item] = self.persona.name

    # Alias for backward compatibility
    update_relationships = update_item_ownership

    def act(self, world: Any, decision: Dict[str, Any], tick: int):
        """
        Delegate action execution to AgentActions module.
        """
        if self.actions:
            self.actions.execute(self, world, decision, tick)
        if hasattr(world, 'broadcast'):
            world.broadcast(self.place, {"actor": self.persona.name, "decision": decision, "tick": tick})

    def move_to(self, world: Any, destination: str, area: Optional[str] = None) -> bool:
        """
        Move the agent to a new location and optionally a specific area if valid.
        """
        if self.movement_controller:
            moved = self.movement_controller.move_to(self, world, destination)
            if moved and area:
                return self.move_to_area(world, destination, area)
            return moved
        return False

    def move_to_area(self, world: Any, place_name: str, area_name: str) -> bool:
        """
        Move the agent to a specific area within a place if valid.
        """
        if hasattr(world, 'places') and place_name in world.places:
            place_obj = world.places[place_name]
            if hasattr(place_obj, 'areas') and area_name in place_obj.areas:
                # Remove agent from current area if present
                for area in place_obj.areas.values():
                    if self.persona.name in area.agents_present:
                        area.remove_agent(self.persona.name)
                # Add agent to new area
                place_obj.areas[area_name].add_agent(self.persona.name)
                self.place = place_name
                # Optionally track current area (add self.area attribute)
                self.area = area_name
                return True
        return False

    def use_item(self, item: Item) -> bool:
        """
        Use an item from the agent's inventory and apply its effects to physio.
        """
        if self.inventory and self.inventory.remove(item, 1):
            # Apply item effects to physio
            if self.physio and hasattr(item, "effects") and isinstance(item.effects, dict):
                for effect, value in item.effects.items():
                    if hasattr(self.physio, effect):
                        old_val = getattr(self.physio, effect)
                        try:
                            setattr(self.physio, effect, old_val + value)
                        except Exception:
                            pass
            return True
        return False

    def initialize_schedule(self, schedule_data: List[Any]):
        """
        Initialize the agent's schedule from the provided data.
        Args:
            schedule_data (list): List of schedule entries (dicts or Appointment objects).
        """
        self.calendar = []
        for entry in schedule_data:
            if isinstance(entry, Appointment):
                self.calendar.append(entry)
            elif isinstance(entry, dict):
                try:
                    appt = Appointment(
                        start_tick=entry.get("start_tick", 0),
                        end_tick=entry.get("end_tick", 0),
                        location=entry.get("location", ""),
                        label=entry.get("label", "")
                    )
                    self.calendar.append(appt)
                except (TypeError, KeyError):
                    pass  # Skip invalid entries

    # ...existing code...

    def add_moodlet(self, moodlet: str, duration: int):
        """Delegate moodlet addition to AgentPhysio."""
        if self.agent_physio:
            self.agent_physio.add_moodlet(moodlet, duration)

    def tick_moodlets(self):
        """Delegate moodlet ticking to AgentPhysio."""
        if self.agent_physio:
            self.agent_physio.tick_moodlets()

    def set_emotional_state(self, state: str):
        """Delegate emotional state setting to AgentPhysio."""
        if self.agent_physio:
            self.agent_physio.set_emotional_state(state)

    def update_relationship(self, other: str, delta: float):
        if self.relationships:
            self.relationships.update_relationship(other, delta)

    def remember_social_interaction(self, interaction: Dict[str, Any]):
        """Add a social interaction to social memory."""
        self.social_memory.append(interaction)

    # ...existing code...


    def apply_moodlet_triggers(self):
        """Delegate moodlet triggers to AgentPhysio."""
        if self.agent_physio:
            self.agent_physio.apply_moodlet_triggers()
