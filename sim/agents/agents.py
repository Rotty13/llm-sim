"""
agents.py

Defines agent classes and data structures for llm-sim simulation.
Contains Persona, Physio, and Agent dataclasses for modeling agent behavior,
physiological state, and decision-making.

Key Classes:
- Persona: Represents an agent's identity, job, values, goals, and personality traits.
- Physio: Represents an agent's physiological state (hunger, energy, stress, mood, etc.).
- Agent: Main agent class with decision-making, memory, inventory, and movement capabilities.

Key Constants:
- JOB_SITE: Dictionary mapping job names to expected work locations.

LLM Usage:
- Uses sim.llm.llm_ollama for conversation and decision-making with LLM.

CLI Arguments:
- None directly; agents are managed by simulation scripts and world modules.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, TYPE_CHECKING

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

# Dictionary mapping job names to expected work locations
JOB_SITE = {
    "chef": "Restaurant",
    "teacher": "School",
    "doctor": "Hospital",
    "nurse": "Hospital",
    "engineer": "Office",
    "programmer": "Office",
    "artist": "Studio",
    "musician": "Studio",
    "writer": "Home",
    "farmer": "Farm",
    "clerk": "Store",
    "shopkeeper": "Store",
    "baker": "Bakery",
    "bartender": "Bar",
    "librarian": "Library",
    "mechanic": "Garage",
}

def parse_action_payload(action_str: str) -> Optional[Dict[str, Any]]:
    """
    Parse an action string and return its payload/params.
    Wrapper around parse_action for backward compatibility.
    """
    try:
        _, params = parse_action(action_str)
        return params if params else None
    except (TypeError, ValueError):
        return None


@dataclass
class Agent:
    # Required fields (no defaults - must be provided)
    persona: Persona
    
    # Optional fields with defaults
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
            for key, cls in module_map.items():
                enabled = self.config.get(key, True)
                setattr(self, key, cls() if enabled else None)
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
        self.agent_plan_logic = AgentPlanLogic(self)




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
        Update agent state each tick: decay needs (with trait effects), update mood, and check aspirations.
        """
        personality = self.persona.get_personality()
        # Delegate to agent_physio module
        self.agent_physio.decay_needs(traits=personality.traits)
        # ...original mood/aspiration/plan logic remains for now...
        self.agent_physio.apply_moodlet_triggers()
        self.agent_physio.tick_moodlets()
        # ...original emotional state logic remains for now...
        # Delegate trait-driven plan logic
        if self.physio:
            self.agent_plan_logic.update_plan(personality, self.physio)

    def perform_action(self, action: str, world: Any, tick: int):
        """
        Perform the given action in the simulation context.
        Args:
            action: Action string (e.g., 'MOVE', 'EAT', etc.)
            world: The simulation world object
            tick: Current simulation tick
        """
        if action.startswith("MOVE"):
            payload = parse_action_payload(action)
            if payload:
                dest = payload.get("to")
                if dest:
                    self.place = dest
                print(f"Agent {self.persona.name} performs action: {action} at tick {tick}")

    def serialize_state(self) -> dict:
        """Serialize agent state for saving."""
        physio_state = {}
        if self.physio:
            physio_state = {
                "hunger": getattr(self.physio, "hunger", None),
                "energy": getattr(self.physio, "energy", None),
                "stress": getattr(self.physio, "stress", None),
                "mood": getattr(self.physio, "mood", None),
                "social": getattr(self.physio, "social", None),
                "fun": getattr(self.physio, "fun", None),
                "hygiene": getattr(self.physio, "hygiene", None),
                "comfort": getattr(self.physio, "comfort", None),
                "bladder": getattr(self.physio, "bladder", None),
            }
        return {
            "persona": {
                "name": self.persona.name,
                "age": self.persona.age,
                "job": self.persona.job,
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
            "alive": self.alive,
            "time_of_death": self.time_of_death,
            "relationships": self.relationships,
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
        if "physio" in state:
            for key, value in state["physio"].items():
                if hasattr(self.physio, key):
                    setattr(self.physio, key, value)

    def add_money(self, amount: int):
        """Add money to the agent's inventory."""
        if self.inventory:
            self.inventory.add_item("money", amount)

    def remove_money(self, amount: int) -> bool:
        """Remove money from the agent's inventory. Returns True if successful."""
        if self.inventory and self.inventory.get_quantity("money") >= amount:
            self.inventory.remove_item("money", amount)
            return True
        return False

    def step_interact(
        self, world: Any, participants: list, obs: str, tick: int,
        start_dt: Optional[datetime], incoming_message: Optional[dict],
        loglist: Optional[list] = None
    ):
        """
        Cohesive step: agent converses, decays needs, updates moodlets, decides, and acts in the world.
        Returns the conversation decision dict.
        Safely handles disabled modules.
        """
        # Decay needs at each tick
        if self.physio:
            self.physio.decay_needs()
        # Update moodlets
        self.tick_moodlets()
        # Conversation step
        conv_decision = self.decide_conversation(participants, obs, tick, incoming_message, start_dt=start_dt, loglist=loglist)
        if conv_decision and "new_mood" in conv_decision and self.physio:
            self.physio.mood = conv_decision["new_mood"]
        if conv_decision and "memory_write" in conv_decision and conv_decision["memory_write"] and self.memory_manager:
            self.memory_manager.write_memory(MemoryItem(t=tick, kind="episodic", text=conv_decision["memory_write"], importance=0.5))
        # Action step
        action_decision = self.decide(world, obs, tick, start_dt)
        self.act(world, action_decision, tick)
        return conv_decision

    def decide_conversation(
        self, participants: List[Any], obs: str, tick: int,
        incoming_message: Optional[dict], start_dt: Optional[datetime] = None,
        loglist: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Decide on a conversational response using LLM, considering conversation history.
        """
        # SYSTEM prompt for conversation
        system_prompt = (
            "You are a human engaged in a conversation. "
            "You are not being simulated or in a simulation. "
            "You are yourself and your memories are real.\n"
            "If you must recall something in your distant past or childhood, "
            "you may invent it. Don't reference specific names or places.\n"
            "Respond as naturally as possible, considering your persona, "
            "context, and conversation history. 1-3 sentences only.\n"
            "Return ONLY JSON with keys: reply, private_thought, memory_write (nullable).\n"
            "Example: {\"to\":\"David\",\"reply\":\"Hello! How can I help you?\"," +
            "\"private_thought\":\"I feel helpful.\",\"memory_write\":\"I greeted someone.\"," +
            "\"new_mood\":\"happy\"}\n"
        )

        # Build conversation history string
        history_str = "\n".join([
            f"{entry['role']}: {entry['content']}"
            for entry in self.conversation_history[-15:]
        ])

        # Build memory strings
        def format_memories(query: str) -> str:
            # Use episodic memory for now
            if self.memory and hasattr(self.memory, 'get_episodic'):
                memories = self.memory.get_episodic()[:5]
                return ", ".join(str(m) for m in memories)
            return ""

        # USER prompt for conversation
        user_prompt = (
            f"You are {self.persona.name} (job: {self.persona.job}, "
            f"city: {self.persona.city}) Bio: {self.persona.bio}.\n" +
            (f"The date is {now_str(tick, start_dt).split()[0]}.\n" if start_dt else "") +
            f"Participants: {', '.join(p.persona.name for p in participants if p != self)}.\n" +
            f"Observations: {obs}\n\n" +
            (f"Time {now_str(tick, start_dt)}. " if start_dt else "") +
            f"Location {self.place}. Mood {getattr(self.physio, 'mood', 'unknown')}.\n" +
            f"Conversation history:\n{history_str}\n" +
            f"My values: {', '.join(self.persona.values)}.\n" +
            f"My goals: {', '.join(self.persona.goals)}.\n" +
            f"I remember: {format_memories('conversation')}\n" +
            f"I remember: {format_memories('life')}\n" +
            f"I remember: {format_memories('recent')}\n" +
            f"Incoming message: {json.dumps(incoming_message)}\n\n" +
            "Craft a thoughtful and context-aware reply.\n"
        )

        out = llm.chat_json(user_prompt, system=system_prompt, max_tokens=256)
        # Sanity check
        if not isinstance(out, dict):
            out = {"reply": "Sorry, I didn't understand.", "private_thought": None, "memory_write": None}
        # Update conversation history
        if incoming_message is not None:
            msg_content = json.dumps(incoming_message) if isinstance(incoming_message, dict) else str(incoming_message)
            self.conversation_history.append({"role": "user", "content": msg_content})
        out['from'] = self.persona.name
        self.conversation_history.append({"role": "agent", "content": json.dumps(out)})
        if loglist is not None:
            loglist.append(out)
        return out

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
        Enhanced decision-making logic for agents, including rule-based and probabilistic choices.
        """
        # Check and enforce schedule
        move_command = enforce_schedule(self.calendar, self.place, tick, self.busy_until)
        if move_command:
            payload = parse_action_payload(move_command)
            if payload:
                return {"action": "MOVE", "params": {"to": payload.get("to", "")}, "private_thought": "I need to move to my appointment."}

        # Rule-based decision-making
        if self.physio:
            if getattr(self.physio, 'hunger', 0) > 0.8:
                return {"action": "EAT", "private_thought": "I'm feeling very hungry."}
            elif getattr(self.physio, 'energy', 1) < 0.3:
                return {"action": "SLEEP", "private_thought": "I'm too tired to continue."}
            elif getattr(self.physio, 'stress', 0) > 0.5:
                return {"action": "RELAX", "private_thought": "I need to relax and reduce my stress."}
            elif getattr(self.physio, 'fun', 1) < 0.3:
                return {"action": "EXPLORE", "private_thought": "I'm bored and need to have some fun."}
            elif getattr(self.physio, 'social', 1) < 0.3:
                # --- Social interaction decision using preference_to_interact ---
                traits = self.persona.traits if hasattr(self.persona, 'traits') else {}
                E_self = traits.get("extraversion", 4)
                A_self = traits.get("agreeableness", 4)
                N_self = traits.get("neuroticism", 4)
                # Dummy partner traits (could be replaced with actual nearby agent)
                E_partner = 4
                A_partner = 4
                N_partner = 4
                familiarity = self.relationships.get_relationship("dummy_partner").get("familiarity", 3) if self.relationships else 3
                attractiveness = 3
                pref_score = preference_to_interact(E_self, A_self, N_self, E_partner, A_partner, N_partner, familiarity, attractiveness)
                if pref_score >= 4:
                    return {"action": "SAY", "private_thought": f"My preference to interact is {pref_score}, I want to talk to someone.", "params": {}}
                else:
                    return {"action": "IDLE", "private_thought": f"My preference to interact is low ({pref_score}), so I won't socialize now."}

        # Incorporate persona values, goals, and traits into decision-making
        traits = self.persona.traits if hasattr(self.persona, 'traits') else {}
        # Conscientiousness: more likely to work
        if traits.get("conscientiousness", 0.5) > 0.7 and random.random() < traits["conscientiousness"]:
            return {"action": "WORK", "private_thought": "My conscientiousness drives me to work diligently."}
        # Openness: more likely to explore
        if traits.get("openness", 0.5) > 0.6 and random.random() < traits["openness"]:
            return {"action": "EXPLORE", "private_thought": "My openness makes me want to explore new things."}
        # Extraversion: more likely to socialize
        if traits.get("extraversion", 0.5) > 0.6 and random.random() < traits["extraversion"]:
            return {"action": "SAY", "private_thought": "I feel like socializing with others.", "params": {}}
        # Neuroticism: more likely to relax
        if traits.get("neuroticism", 0.5) > 0.6 and random.random() < traits["neuroticism"]:
            return {"action": "RELAX", "private_thought": "I need to relax and manage my stress."}
        # Agreeableness: more likely to help/interact
        if traits.get("agreeableness", 0.5) > 0.6 and random.random() < traits["agreeableness"]:
            return {"action": "INTERACT", "private_thought": "I want to help or interact with others.", "params": {"action_type": "help"}}

        # Existing value/goal-based logic
        if "ambition" in self.persona.values and "achieve goal" in self.persona.goals:
            if random.random() < 0.3:
                return {"action": "WORK", "private_thought": "I feel motivated to work on my goals."}
        if "curiosity" in self.persona.values:
            if random.random() < 0.4:
                return {"action": "EXPLORE", "private_thought": "My curiosity drives me to explore."}
        if self.physio and getattr(self.physio, 'stress', 0) > 0.7 and "relaxation" in self.persona.values:
            return {"action": "RELAX", "private_thought": "I value relaxation and need to reduce stress."}

        # Probabilistic decision-making for exploration
        if random.random() < 0.2:
            return {"action": "EXPLORE", "private_thought": "I feel like exploring the area."}

        # Default action
        return {"action": "IDLE", "private_thought": "I have nothing to do right now."}

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
        Perform the action decided by the agent.
        Supports actions: MOVE, EAT, SLEEP, RELAX, EXPLORE, WORK, SAY, INTERACT, THINK, CONTINUE.
        """
        from sim.actions.actions import get_action_duration, get_action_effects

        action = decision.get("action", "").upper()
        params = decision.get("params", {})

        # Get action duration and effects
        duration = get_action_duration(action, params)
        effects = get_action_effects(action, params)

        # Modulate action effects by personality traits
        traits = self.persona.traits
        if self.physio:
            if action == "RELAX":
                # More extraverted/agreeable agents relax more efficiently
                relax_boost = 0.1 * (traits.get("extraversion", 0.5) + traits.get("agreeableness", 0.5) - 1.0)
                self.physio.stress = max(0.0, self.physio.stress + effects.get("stress", -0.2) + relax_boost)
            elif action == "WORK":
                # Conscientiousness increases work energy cost, neuroticism increases stress
                work_penalty = 0.05 * (traits.get("conscientiousness", 0.5) - 0.5)
                stress_penalty = 0.05 * (traits.get("neuroticism", 0.5) - 0.5)
                self.physio.energy = max(0.0, self.physio.energy + effects.get("energy", -0.15) - work_penalty)
                self.physio.stress = min(1.0, self.physio.stress + effects.get("stress", 0.1) + stress_penalty)
            elif action == "SAY":
                # Extraversion increases social gain
                social_boost = 0.1 * (traits.get("extraversion", 0.5) - 0.5)
                self.physio.social = min(1.0, self.physio.social + social_boost)

            if action == "MOVE":
                destination = params.get("to")
                if destination and self.movement_controller:
                    self.movement_controller.move_to(self, world, destination)
                self.busy_until = tick + duration

            elif action == "EAT":
                self.physio.hunger = max(0.0, self.physio.hunger + effects.get("hunger", -0.5))
                self.physio.energy = min(1.0, self.physio.energy + effects.get("energy", 0.1))
                self.busy_until = tick + duration

            elif action == "SLEEP":
                self.physio.energy = min(1.0, self.physio.energy + effects.get("energy", 0.8))
                self.physio.stress = max(0.0, self.physio.stress + effects.get("stress", -0.3))
                self.busy_until = tick + duration

            elif action == "RELAX":
                self.physio.stress = max(0.0, self.physio.stress + effects.get("stress", -0.2))
                self.physio.energy = min(1.0, self.physio.energy + effects.get("energy", 0.05))
                self.busy_until = tick + duration

            elif action == "EXPLORE":
                self.physio.energy = max(0.0, self.physio.energy + effects.get("energy", -0.1))
                self.physio.stress = max(0.0, self.physio.stress + effects.get("stress", -0.05))
                self.busy_until = tick + duration

            elif action == "WORK":
                # Validate work location
                if self._work_allowed_here(world):
                    self.physio.energy = max(0.0, self.physio.energy + effects.get("energy", -0.15))
                    self.physio.stress = min(1.0, self.physio.stress + effects.get("stress", 0.1))
                    self.physio.hunger = min(1.0, self.physio.hunger + effects.get("hunger", 0.1))
                    self.busy_until = tick + duration
                    # Add work reward (money)
                    money_item = ITEMS.get("money")
                    if money_item and self.inventory:
                        reward = params.get("reward", 10)
                        self.inventory.add_item("money", reward)
                else:
                    # Cannot work here, reduce to think action
                    self.busy_until = tick + 1

            elif action == "SAY":
                text = params.get("text", "")
                target = params.get("to")
                self.physio.energy = max(0.0, self.physio.energy + effects.get("energy", -0.01))
                self.busy_until = tick + duration
                # Record in memory
                if text and self.memory_manager:
                    self.memory_manager.write_memory(MemoryItem(
                        t=tick,
                        kind="episodic",
                        text=f"I said '{text}'" + (f" to {target}" if target else ""),
                        importance=0.3
                    ))

            elif action == "INTERACT":
                target = params.get("target", "")
                action_type = params.get("action_type", "observe")
                self.physio.energy = max(0.0, self.physio.energy + effects.get("energy", -0.02))
                self.busy_until = tick + duration
                # Record interaction in memory
                if target and self.memory_manager:
                    self.memory_manager.write_memory(MemoryItem(
                        t=tick,
                        kind="episodic",
                        text=f"I {action_type}d {target}",
                        importance=0.4
                    ))

            elif action == "THINK":
                self.physio.energy = max(0.0, self.physio.energy + effects.get("energy", -0.01))
                self.busy_until = tick + duration

            elif action == "CONTINUE":
                # Do nothing, maintain current state
                pass

            else:
                # Unknown action, default to think
                self.busy_until = tick + 1

        # Broadcast the action to the world
        if hasattr(world, 'broadcast'):
            world.broadcast(self.place, {"actor": self.persona.name, "action": action, "params": params, "tick": tick})

    def move_to(self, world: Any, destination: str) -> bool:
        """
        Move the agent to a new location if valid.
        """
        if self.movement_controller:
            return self.movement_controller.move_to(self, world, destination)
        return False

    def use_item(self, item: Item) -> bool:
        """
        Use an item from the agent's inventory.
        """
        if self.inventory and self.inventory.has_item(item.id):
            self.inventory.remove_item(item.id, 1)
            if item.effects and self.physio:
                for effect, value in item.effects.items():
                    if hasattr(self.physio, effect):
                        current_value = getattr(self.physio, effect)
                        setattr(self.physio, effect, max(0.0, current_value + value))
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
        """Add or refresh a moodlet for a given duration (in ticks)."""
        if self.physio and hasattr(self.physio, 'moodlets'):
            self.physio.moodlets[moodlet] = duration

    def tick_moodlets(self):
        """Decrement moodlet durations and remove expired ones."""
        if self.physio and hasattr(self.physio, 'moodlets'):
            expired = [k for k, v in self.physio.moodlets.items() if v <= 1]
            for k in expired:
                del self.physio.moodlets[k]
            for k in self.physio.moodlets:
                self.physio.moodlets[k] -= 1

    def set_emotional_state(self, state: str):
        """Set the agent's current emotional state."""
        if self.physio:
            self.physio.emotional_state = state

    def update_relationship(self, other: str, delta: float):
        if self.relationships:
            self.relationships.update_relationship(other, delta)

    def remember_social_interaction(self, interaction: Dict[str, Any]):
        """Add a social interaction to social memory."""
        self.social_memory.append(interaction)

    # ...existing code...

    def personality_memory_importance(self, item: MemoryItem) -> float:
        """
        Adjust memory importance by personality traits (e.g., neuroticism boosts negative, openness boosts novel).
        """
        traits = self.persona.traits
        importance = item.importance
        if "sad" in item.text or "failure" in item.text:
            importance += 0.2 * traits.get("neuroticism", 0.5)
        if "new" in item.text or "explore" in item.text:
            importance += 0.2 * traits.get("openness", 0.5)
        if "friend" in item.text or "talk" in item.text:
            importance += 0.2 * traits.get("extraversion", 0.5)
        return max(0.0, min(1.0, importance))

    def apply_moodlet_triggers(self):
        """Apply moodlets based on agent state and recent events."""
        if not self.physio:
            return
        # Hunger moodlet
        if getattr(self.physio, 'hunger', 0) > 0.9:
            self.add_moodlet("starving", 5)
        # Energy moodlet
        if getattr(self.physio, 'energy', 1) < 0.1:
            self.add_moodlet("exhausted", 5)
        # Social moodlet
        if getattr(self.physio, 'social', 1) < 0.1:
            self.add_moodlet("lonely", 5)
        # Fun moodlet
        if getattr(self.physio, 'fun', 1) < 0.1:
            self.add_moodlet("bored", 5)
        # Hygiene moodlet
        if getattr(self.physio, 'hygiene', 1) < 0.1:
            self.add_moodlet("dirty", 5)
        # Comfort moodlet
        if getattr(self.physio, 'comfort', 1) < 0.1:
            self.add_moodlet("uncomfortable", 5)
        # Bladder moodlet
        if getattr(self.physio, 'bladder', 1) < 0.05:
            self.add_moodlet("desperate", 5)
        # Stress moodlet
        if getattr(self.physio, 'stress', 0) > 0.9:
            self.add_moodlet("overwhelmed", 5)
