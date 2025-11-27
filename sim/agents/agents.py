from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
import json, string
from typing import TYPE_CHECKING
import random

from ..llm.llm_ollama import AI_ASSISTANT_SYSTEM
from ..memory.memory import MemoryStore, MemoryItem
from ..actions.actions import normalize_action
from ..world.world import World
from ..scheduler.scheduler import Appointment, enforce_schedule
from ..inventory.inventory import Inventory
from sim.llm import llm_ollama
from sim.inventory.inventory import Item

from .controllers import BaseController, LogicController
from .memory_manager import MemoryManager
from .inventory_handler import InventoryHandler
from .decision_controller import DecisionController
from .movement_controller import MovementController

llm = llm_ollama.LLM()

def now_str(tick: int, start_dt=None) -> str:
    """
    Returns a formatted time string for the given tick and start_dt.
    If start_dt is None, returns local time as HH:MM.
    """
    if start_dt is not None:
        from sim.utils.utils import now_str
        return now_str(tick, start_dt)
    return f"{(tick * 5) // 60:02d}:{(tick * 5) % 60:02d}"

@dataclass
class Persona:
    name: str
    age: int
    job: str
    city: str
    bio: str
    values: List[str]
    goals: List[str]

@dataclass
class Physio:
    energy: float = 1.0
    hunger: float = 0.2
    stress: float = 0.2
    mood: str = "neutral"

JOB_SITE = {"barista":"Cafe", "junior dev":"Office", "developer":"Office", "engineer":"Office"}


@dataclass
class Agent:
    persona: Persona
    place: str
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

    busy_until: int = 0  # Tick until which the agent is busy

    def deposit_item_to_place(self, world: 'World', item_id: str, qty: int = 1) -> bool:
        """
        Delegate depositing items to the InventoryHandler.
        Updates busy_until to reflect the time taken for the action.
        """
        place_name = world.get_agent_location(self.persona.name)
        if not place_name:
            return False

        place = world.places.get(place_name)
        if not place:
            return False

        success = self.inventory_handler.deposit_item_to_place(self, place, item_id, qty)
        if success:
            self.busy_until += 5  # Example: Depositing takes 5 ticks
        return success

    def withdraw_item_from_place(self, world: 'World', item_id: str, qty: int = 1) -> bool:
        """
        Delegate withdrawing items to the InventoryHandler.
        Updates busy_until to reflect the time taken for the action.
        """
        place_name = world.get_agent_location(self.persona.name)
        if not place_name:
            return False

        place = world.places.get(place_name)
        if not place:
            return False

        success = self.inventory_handler.withdraw_item_from_place(self, place, item_id, qty)
        if success:
            self.busy_until += 5  # Example: Withdrawing takes 5 ticks
        return success

    def step_interact(self, world: 'World', participants: list, obs: str, tick: int, start_dt, incoming_message: Optional[dict], loglist: Optional[list] = None):
        """
        Cohesive step: agent converses, decides, and acts in the world.
        Returns the conversation decision dict.
        """
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

    def decide_conversation(self, participants: List[Agent],obs: str, tick: int, incoming_message: Optional[dict],start_dt: Optional[datetime] = None,   loglist: Optional[List[Dict[str, Any]]] = None) -> Dict[str,Any]:
        """
        Decide on a conversational response using LLM, considering conversation history.
        """
        # SYSTEM prompt for conversation
        system_prompt = (
            "You are a human engaged in a conversation. You are not being simulated or in a simulation. You are yourself and your memories are real.\n"
            "If you must recall something in your distant past or childhood, you may invent it. don't reference specific names or places.\n"
            "Respond as naturally as possible, considering your persona, context, and conversation history. 1-3 sentences only.\n"
            "Return ONLY JSON with keys: reply, private_thought, memory_write (nullable).\n"
            "Example: {\"to\":\"David\",\"reply\":\"Hello! How can I help you?\",\"private_thought\":\"I feel helpful.\",\"memory_write\":\"I greeted someone.\",\"new_mood\":\"happy\"}\n"
        )

        # Build conversation history string
        history_str = "\n".join([
            f"{entry['role']}: {entry['content']}" for entry in self.conversation_history[-15:]
        ])

        # USER prompt for conversation
        user_prompt = (
                (
                    f"You are {self.persona.name} (job: {self.persona.job}, city: {self.persona.city}) Bio: {self.persona.bio}.\n" +
                    (f"The date is {now_str(tick,start_dt).split()[0]}.\n" if start_dt else "") +
                    f"Participants: {', '.join(p.persona.name for p in participants if p != self)}.\n" +
                    f"Observations: {obs}\n\n" +
                    f"Time {now_str(tick,start_dt)}. " +
                    f"Location {self.place}. Mood {self.physio.mood}.\n" +
                    f"Conversation history:\n{history_str}\n" +
                    f"My values: {', '.join(self.persona.values)}.\n" +
                    f"My goals: {', '.join(self.persona.goals)}.\n" +
                    f"I remember: " + ", ".join(f"[{now_str(m.t,start_dt)}] {m.kind}: {m.text}" for m in self.memory.recall("conversation", k=5)) + "\n" +
                    f"I remember: " + ", ".join(f"[{now_str(m.t,start_dt)}] {m.kind}: {m.text}" for m in self.memory.recall("life", k=5)) + "\n" +
                    f"I remember: " + ", ".join(f"[{now_str(m.t,start_dt)}] {m.kind}: {m.text}" for m in self.memory.recall("recent", k=5)) + "\n" +
                    f"Incoming message: {json.dumps(incoming_message)}\n\n" +
                    "Craft a thoughtful and context-aware reply.\n"
                )
        )

        out = llm.chat_json(user_prompt, system=system_prompt, max_tokens=256)
        # sanity carve
        if not isinstance(out, dict):
            out = {"reply":"Sorry, I didn't understand.","private_thought":None,"memory_write":None}
        # Update conversation history
        if incoming_message is not None:
            # Handle new format: {'to': ..., 'from': ..., 'text': ...}
            msg_role = "user"
            msg_content = ""
            if isinstance(incoming_message, dict):
                # Compose a readable string for the message
                msg_from = incoming_message.get("from", "Unknown")
                msg_to = incoming_message.get("to", "Unknown")
                msg_text = incoming_message.get("text", "")
                msg_content = f"From: {msg_from}, To: {msg_to}, Text: {msg_text}"
            else:
                msg_content = str(incoming_message)
            self.conversation_history.append({"role": msg_role, "content": json.dumps(incoming_message)})
        out['from']=self.persona.name
        self.conversation_history.append({"role": "agent", "content": json.dumps(out)})
        if loglist is not None:
            loglist.append(out)
        return out

    # runtime
    busy_until: int = -1
    _last_say_tick: int = -999
    _last_diary_tick: int = -999
    _last_diary: str = ""

    def add_observation(self, text: str):
        self.memory_manager.add_observation(text)

    def _maybe_write_diary(self, text: str, tick: int):
        if not text:
            return
        if (tick - self._last_diary_tick) < 6:
            return
        sim = SequenceMatcher(None, self.memory_manager._norm_text(self._last_diary), self.memory_manager._norm_text(text)).ratio()
        if sim < 0.93:
            self.memory_manager.write_memory(MemoryItem(t=tick, kind="autobio", text=text, importance=0.6))
            self._last_diary, self._last_diary_tick = text, tick

    def _work_allowed_here(self, world:World) -> bool:
        expected = JOB_SITE.get(self.persona.job)
        return bool(expected) and self.place == expected

    def _eat_allowed_here(self, world:World) -> bool:
        p = world.places[self.place]
        return "food" in p.capabilities or "food_home" in p.capabilities

    def decide(self, world: World, obs_text: str, tick: int, start_dt) -> Dict[str, Any]:
        """
        Enhanced decision-making logic for agents, including rule-based and probabilistic choices.

        Notes:
            - Decision logic should only reside in the controller.
            - Enforces schedules using the enforce_schedule function.
        """
        # Check and enforce schedule
        move_command = enforce_schedule(self.calendar, self.place, tick, self.busy_until)
        if move_command:
            return {"action": "MOVE", "params": {"to": move_command.split('"')[3]}, "private_thought": "I need to move to my appointment."}

        # Rule-based decision-making
        if self.physio.hunger > 0.8:
            return {"action": "EAT", "private_thought": "I'm feeling very hungry."}
        elif self.physio.energy < 0.3:
            return {"action": "SLEEP", "private_thought": "I'm too tired to continue."}
        elif self.physio.stress > 0.5:
            return {"action": "RELAX", "private_thought": "I need to relax and reduce my stress."}

        # Incorporate persona values and goals into decision-making
        if "ambition" in self.persona.values and "achieve goal" in self.persona.goals:
            if random.random() < 0.3:  # 30% chance to work on a goal
                return {"action": "WORK", "private_thought": "I feel motivated to work on my goals."}

        if "curiosity" in self.persona.values:
            if random.random() < 0.4:  # 40% chance to explore
                return {"action": "EXPLORE", "private_thought": "My curiosity drives me to explore."}

        # Add more nuanced rules based on persona and environment
        if self.physio.stress > 0.7 and "relaxation" in self.persona.values:
            return {"action": "RELAX", "private_thought": "I value relaxation and need to reduce stress."}

        # Probabilistic decision-making for exploration
        if random.random() < 0.2:  # 20% chance to explore
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

    def update_relationships(self, world: World):
        """
        Updates item ownership using the world's `item_ownership` dictionary.
        """
        for item_stack in self.inventory.stacks:
            world.item_ownership[item_stack.item.id] = self.persona.name

    def act(self, world: World, decision: Dict[str, Any], tick: int):
        """
        Perform the action decided by the agent.
        Supports actions: MOVE, EAT, SLEEP, RELAX, EXPLORE, WORK, SAY, INTERACT, THINK, CONTINUE.
        """
        from sim.actions.actions import get_action_duration, get_action_effects, ACTION_DURATIONS
        
        action = decision.get("action", "").upper()
        params = decision.get("params", {})
        
        # Get action duration and effects
        duration = get_action_duration(action, params)
        effects = get_action_effects(action, params)

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
                from sim.inventory.inventory import ITEMS
                money_item = ITEMS.get("money")
                if money_item:
                    reward = params.get("reward", 10)
                    self.inventory.add(money_item, reward)
            else:
                # Cannot work here, reduce to think action
                action = "THINK"
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
        world.broadcast(self.place, {"actor": self.persona.name, "action": action, "params": params, "tick": tick})

    def move_to(self, world: World, destination: str) -> bool:
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

    def initialize_schedule(self, schedule_data):
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