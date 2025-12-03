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
from sim.llm import llm_ollama

from sim.agents.controllers import LogicController
from sim.agents.memory_manager import MemoryManager
from sim.agents.inventory_handler import InventoryHandler
from sim.agents.decision_controller import DecisionController
from sim.agents.movement_controller import MovementController

if TYPE_CHECKING:
    from sim.world.world import World

# LLM instance for agent conversations
llm = llm_ollama.LLM()

# Job to work site mapping
JOB_SITE: Dict[str, str] = {
    "barista": "Cafe",
    "developer": "Office",
    "chef": "Restaurant",
    "artist": "Studio",
    "teacher": "School",
    "doctor": "Hospital",
    "nurse": "Hospital",
    "clerk": "Store",
    "librarian": "Library",
}

# Default age transitions for life stages
DEFAULT_AGE_TRANSITIONS: Dict[str, int] = {
    "child": 0,
    "teen": 13,
    "adult": 18,
    "elder": 65
}


def parse_action_payload(action_str: str) -> Optional[Dict[str, Any]]:
    """
    Parse the JSON payload from an action string like 'MOVE({"to":"Office"})'.
    Returns None if parsing fails.
    """
    try:
        start = action_str.find("(")
        end = action_str.rfind(")")
        if start != -1 and end != -1 and end > start:
            return json.loads(action_str[start + 1:end])
    except (json.JSONDecodeError, ValueError):
        pass
    return None


@dataclass
class Persona:
    """Represents an agent's identity, personality, and life characteristics."""
    name: str
    age: int
    job: str
    city: str
    bio: str
    values: List[str]
    goals: List[str]
    traits: Dict[str, float] = field(default_factory=dict)
    aspirations: List[str] = field(default_factory=list)
    emotional_modifiers: Dict[str, float] = field(default_factory=dict)
    age_transitions: Dict[str, int] = field(default_factory=dict)
    life_stage: str = "adult"


@dataclass
class Physio:
    """Represents an agent's physiological and emotional state."""
    hunger: float = 0.3
    energy: float = 0.8
    stress: float = 0.2
    mood: str = "neutral"
    social: float = 0.5
    fun: float = 0.5
    moodlets: Dict[str, int] = field(default_factory=dict)
    emotional_state: str = "neutral"
    hygiene: float = 0.8
    comfort: float = 0.8
    bladder: float = 0.8

    def decay_needs(self, traits: Optional[Dict[str, float]] = None):
        """
        Decay physiological needs over time, modulated by personality traits.
        Higher neuroticism increases stress accumulation; conscientiousness slows hunger decay.
        """
        traits = traits or {}
        # Base decay rates
        hunger_decay = 0.02
        energy_decay = 0.01
        stress_decay = 0.01
        hygiene_decay = 0.01
        comfort_decay = 0.01
        bladder_decay = 0.02

        # Trait modulation
        hunger_decay *= (1.0 - 0.3 * traits.get("conscientiousness", 0.5))
        stress_decay *= (1.0 + 0.4 * traits.get("neuroticism", 0.5))
        energy_decay *= (1.0 - 0.2 * traits.get("extraversion", 0.5))

        # Apply decay
        self.hunger = min(1.0, self.hunger + hunger_decay)
        self.energy = max(0.0, self.energy - energy_decay)
        self.stress = min(1.0, self.stress + stress_decay)
        self.social = max(0.0, self.social - 0.01)
        self.fun = max(0.0, self.fun - 0.01)
        self.hygiene = max(0.0, self.hygiene - hygiene_decay)
        self.comfort = max(0.0, self.comfort - comfort_decay)
        self.bladder = max(0.0, self.bladder - bladder_decay)


@dataclass
class Agent:
    """
    Main agent class for llm-sim simulation.

    Combines persona, physiology, memory, inventory, and decision-making
    into a cohesive agent that can interact with the simulated world.
    """
    # Required fields (no default)
    persona: Persona
    place: str

    # Optional fields with defaults
    calendar: List[Appointment] = field(default_factory=list)
    controller: Any = field(default_factory=lambda: LogicController())
    memory: MemoryStore = field(default_factory=MemoryStore)
    physio: Physio = field(default_factory=Physio)
    plan: List[str] = field(default_factory=list)
    inventory: Inventory = field(default_factory=lambda: Inventory(capacity_weight=5.0))
    obs_list: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_manager: MemoryManager = field(default_factory=MemoryManager)
    inventory_handler: InventoryHandler = field(default_factory=InventoryHandler)
    decision_controller: DecisionController = field(default_factory=DecisionController)
    movement_controller: MovementController = field(default_factory=MovementController)
    busy_until: int = 0
    alive: bool = True
    time_of_death: Optional[int] = None
    relationships: Dict[str, float] = field(default_factory=dict)
    social_memory: List[Dict[str, Any]] = field(default_factory=list)

    # Runtime fields (not serialized)
    _last_say_tick: int = field(default=-999, repr=False)
    _last_diary_tick: int = field(default=-999, repr=False)
    _last_diary: str = field(default="", repr=False)

    def tick_update(self, world: Any, tick: int):
        """
        Update agent state each tick: decay needs (with trait effects), update mood, and check aspirations.
        """
        self.physio.decay_needs(traits=self.persona.traits)
        # Mood logic: baseline + emotional reactivity + stress
        base = self.persona.emotional_modifiers.get("baseline_mood", 0.0)
        react = self.persona.emotional_modifiers.get("emotional_reactivity", 0.5)
        mood_val = base + react * (0.5 - self.physio.stress)
        if mood_val > 0.3:
            self.physio.mood = "positive"
        elif mood_val < -0.3:
            self.physio.mood = "negative"
        else:
            self.physio.mood = "neutral"
        # Aspirations: if agent has a long-term goal, nudge plan
        if self.persona.aspirations:
            for asp in self.persona.aspirations:
                if asp == "wealth" and self.physio.energy > 0.5:
                    if "WORK" not in self.plan:
                        self.plan.append("WORK")
                if asp == "friendship" and self.physio.social < 0.7:
                    if "SAY" not in self.plan:
                        self.plan.append("SAY")
                if asp == "exploration" and self.physio.energy > 0.3:
                    if "EXPLORE" not in self.plan:
                        self.plan.append("EXPLORE")

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
            "physio": {
                "hunger": self.physio.hunger,
                "energy": self.physio.energy,
                "stress": self.physio.stress,
                "mood": self.physio.mood,
                "social": self.physio.social,
                "fun": self.physio.fun,
                "hygiene": self.physio.hygiene,
                "comfort": self.physio.comfort,
                "bladder": self.physio.bladder,
            },
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

    def checkpoint_stub(self):
        """Stub for checkpoint/resume logic."""
        pass

    def die(self, tick: int):
        """Mark the agent as deceased and record time of death."""
        self.alive = False
        self.time_of_death = tick

    def mourn_stub(self, deceased_name: str):
        """Stub for mourning/legacy logic when another agent dies."""
        pass

    def receive_income(self, amount: float):
        """Add income to the agent's inventory as money."""
        self.inventory.add(ITEMS["money"], int(amount))

    def perform_job_stub(self):
        """Stub for job/career action logic."""
        pass

    def update_life_stage(self):
        """Update the agent's life stage based on age and persona's age_transitions."""
        # Use persona's age_transitions if defined, otherwise use defaults
        age_transitions = self.persona.age_transitions if self.persona.age_transitions else DEFAULT_AGE_TRANSITIONS
        for stage, threshold in sorted(age_transitions.items(), key=lambda x: x[1], reverse=True):
            if self.persona.age >= threshold:
                self.persona.life_stage = stage
                break

    @property
    def money_balance(self) -> int:
        """Return the agent's current money balance (as quantity of 'money' in inventory)."""
        return self.inventory.get_quantity("money")

    def add_money(self, amount: int):
        """Add money to the agent's inventory."""
        self.inventory.add(ITEMS["money"], amount)

    def remove_money(self, amount: int) -> bool:
        """Remove money from the agent's inventory. Returns True if successful."""
        return self.inventory.remove("money", amount)

    def step_interact(
        self, world: Any, participants: list, obs: str, tick: int,
        start_dt: Optional[datetime], incoming_message: Optional[dict],
        loglist: Optional[list] = None
    ):
        """
        Cohesive step: agent converses, decays needs, updates moodlets, decides, and acts in the world.
        Returns the conversation decision dict.
        """
        # Decay needs at each tick
        self.physio.decay_needs()
        # Update moodlets
        self.tick_moodlets()
        # Conversation step
        conv_decision = self.decide_conversation(participants, obs, tick, incoming_message, start_dt=start_dt, loglist=loglist)
        if conv_decision and "new_mood" in conv_decision:
            self.physio.mood = conv_decision["new_mood"]
        if conv_decision and "memory_write" in conv_decision and conv_decision["memory_write"]:
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
            "you may invent it. don't reference specific names or places.\n"
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
            memories = self.memory.recall(query, k=5)
            return ", ".join(
                f"[{now_str(m.t, start_dt) if start_dt else m.t}] {m.kind}: {m.text}"
                for m in memories
            )

        # USER prompt for conversation
        user_prompt = (
            f"You are {self.persona.name} (job: {self.persona.job}, "
            f"city: {self.persona.city}) Bio: {self.persona.bio}.\n" +
            (f"The date is {now_str(tick, start_dt).split()[0]}.\n" if start_dt else "") +
            f"Participants: {', '.join(p.persona.name for p in participants if p != self)}.\n" +
            f"Observations: {obs}\n\n" +
            (f"Time {now_str(tick, start_dt)}. " if start_dt else "") +
            f"Location {self.place}. Mood {self.physio.mood}.\n" +
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

    def add_observation(self, text: str):
        """Add an observation to the memory manager."""
        self.memory_manager.add_observation(text)

    def _maybe_write_diary(self, text: str, tick: int):
        """Write diary entry if conditions are met (not too similar to last entry)."""
        if not text:
            return
        if (tick - self._last_diary_tick) < 6:
            return
        sim = SequenceMatcher(None, self.memory_manager._norm_text(self._last_diary), self.memory_manager._norm_text(text)).ratio()
        if sim < 0.93:
            self.memory_manager.write_memory(MemoryItem(t=tick, kind="autobio", text=text, importance=0.6))
            self._last_diary, self._last_diary_tick = text, tick

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
        if self.physio.hunger > 0.8:
            return {"action": "EAT", "private_thought": "I'm feeling very hungry."}
        elif self.physio.energy < 0.3:
            return {"action": "SLEEP", "private_thought": "I'm too tired to continue."}
        elif self.physio.stress > 0.5:
            return {"action": "RELAX", "private_thought": "I need to relax and reduce my stress."}
        elif self.physio.fun < 0.3:
            return {"action": "EXPLORE", "private_thought": "I'm bored and need to have some fun."}
        elif self.physio.social < 0.3:
            return {"action": "SAY", "private_thought": "I'm feeling lonely and want to talk to someone.", "params": {}}

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
        if self.physio.stress > 0.7 and "relaxation" in self.persona.values:
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
        for item_stack in self.inventory.stacks:
            world.item_ownership[item_stack.item.id] = self.persona.name

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
            if destination:
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
                if money_item:
                    reward = params.get("reward", 10)
                    self.inventory.add(money_item, reward)
            else:
                # Cannot work here, reduce to think action
                self.busy_until = tick + 1

        elif action == "SAY":
            text = params.get("text", "")
            target = params.get("to")
            self.physio.energy = max(0.0, self.physio.energy + effects.get("energy", -0.01))
            self.busy_until = tick + duration
            # Record in memory
            if text:
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
            if target:
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
        return self.movement_controller.move_to(self, world, destination)

    def use_item(self, item: Item) -> bool:
        """
        Use an item from the agent's inventory.
        """
        if self.inventory.has(item.id):
            self.inventory.remove(item.id, 1)
            if item.effects:
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

    def deposit_item_to_place(self, world: Any, item_name: str, quantity: int) -> bool:
        """
        Deposit an item from agent's inventory to the current place's inventory.
        """
        if self.inventory.get_quantity(item_name) >= quantity:
            self.inventory.remove(item_name, quantity)
            place_obj = world.places[self.place]
            item_obj = ITEMS[item_name]
            place_obj.inventory.add(item_obj, quantity)
            return True
        return False

    def withdraw_item_from_place(self, world: Any, item_name: str, quantity: int) -> bool:
        """
        Withdraw an item from the current place's inventory to agent's inventory.
        """
        place_obj = world.places[self.place]
        if place_obj.inventory.get_quantity(item_name) >= quantity:
            place_obj.inventory.remove(item_name, quantity)
            item_obj = ITEMS[item_name]
            self.inventory.add(item_obj, quantity)
            return True
        return False

    def add_moodlet(self, moodlet: str, duration: int):
        """Add or refresh a moodlet for a given duration (in ticks)."""
        self.physio.moodlets[moodlet] = duration

    def tick_moodlets(self):
        """Decrement moodlet durations and remove expired ones."""
        expired = [k for k, v in self.physio.moodlets.items() if v <= 1]
        for k in expired:
            del self.physio.moodlets[k]
        for k in self.physio.moodlets:
            self.physio.moodlets[k] -= 1

    def set_emotional_state(self, state: str):
        """Set the agent's current emotional state."""
        self.physio.emotional_state = state

    def update_relationship(self, other: str, delta: float):
        """Update relationship score with another agent."""
        self.relationships[other] = self.relationships.get(other, 0.0) + delta

    def remember_social_interaction(self, interaction: Dict[str, Any]):
        """Add a social interaction to social memory."""
        self.social_memory.append(interaction)

    def group_conversation_stub(self, participants: list, topic: str):
        """Stub for group conversation mechanics."""
        pass

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
