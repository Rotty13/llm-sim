"""
actions.py

Defines the normalize_action function for converting action representations to a canonical DSL string. Used throughout the simulation for agent and system actions.

Supported Actions:
    - SAY: Agent says something (params: text, to)
    - MOVE: Agent moves to location (params: to)
    - INTERACT: Agent interacts with object/agent (params: target, action_type)
    - THINK: Agent thinks privately
    - PLAN: Agent plans ahead
    - SLEEP: Agent sleeps to restore energy
    - EAT: Agent eats to reduce hunger
    - WORK: Agent works at current location (params: duration, task)
    - CONTINUE: Agent continues current activity
    - RELAX: Agent relaxes to reduce stress
    - EXPLORE: Agent explores the area
    - BUY: Agent buys from vendor (params: item, qty)
    - SELL: Agent sells to vendor (params: item, qty)
"""
from __future__ import annotations
import json
import re
from typing import Any, Dict, Optional
from dataclasses import dataclass

ACTION_RE = re.compile(r'^(SAY|MOVE|INTERACT|THINK|PLAN|SLEEP|EAT|WORK|CONTINUE|RELAX|EXPLORE|BUY|SELL)(\((.*)\))?$')

# Action duration in ticks (5 minutes per tick)
ACTION_DURATIONS = {
    "SAY": 1,
    "MOVE": 2,
    "INTERACT": 2,
    "THINK": 1,
    "PLAN": 2,
    "SLEEP": 24,  # 2 hours
    "EAT": 3,     # 15 minutes
    "WORK": 12,   # 1 hour default
    "CONTINUE": 0,
    "RELAX": 4,   # 20 minutes
    "EXPLORE": 6, # 30 minutes
    "BUY": 1,
    "SELL": 1,
}

# Action costs (physio effects)
ACTION_COSTS = {
    "SAY": {"energy": -0.01, "stress": 0.02},
    "MOVE": {"energy": -0.05},
    "INTERACT": {"energy": -0.02, "stress": 0.01},
    "THINK": {"energy": -0.01},
    "PLAN": {"energy": -0.02},
    "SLEEP": {"energy": 0.8, "stress": -0.3},
    "EAT": {"hunger": -0.5, "energy": 0.1},
    "WORK": {"energy": -0.15, "stress": 0.1, "hunger": 0.1},
    "CONTINUE": {},
    "RELAX": {"stress": -0.2, "energy": 0.05},
    "EXPLORE": {"energy": -0.1, "stress": -0.05},
    "BUY": {"energy": -0.01},
    "SELL": {"energy": -0.01},
}


@dataclass
class ActionResult:
    """Result of executing an action."""
    success: bool
    message: str
    duration: int = 0
    effects: Dict[str, float] = None
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = {}


def normalize_action(action: Any) -> str:
    """Accept dict or string, return canonical DSL string."""
    if isinstance(action, dict):
        atype = (action.get("type") or action.get("action") or "THINK").strip().upper()
        payload = {k: v for k, v in action.items() if k not in ("type", "action")}
        return f"{atype}({json.dumps(payload)})" if payload else f"{atype}()"
    if isinstance(action, str):
        s = action.strip().upper()
        if s in ACTION_DURATIONS:
            return f"{s}()"
        m = ACTION_RE.match(s)
        if m:
            return f"{m.group(1)}{m.group(2) or '()'}"
    return f'THINK({{"note":"invalid action format: {action}"}})'


def parse_action(action_str: str) -> tuple:
    """
    Parse an action DSL string into action type and parameters.
    
    Args:
        action_str: Action string in DSL format like "MOVE({"to":"Cafe"})"
    
    Returns:
        Tuple of (action_type: str, params: dict)
    """
    if not isinstance(action_str, str):
        return ("THINK", {"note": "parse_failed"})
    
    stripped = action_str.strip()
    m = ACTION_RE.match(stripped.upper())
    if not m:
        return ("THINK", {"note": "parse_failed"})
    
    action_type = m.group(1)
    
    # Extract params from original string to preserve case
    params = {}
    paren_start = stripped.find("(")
    paren_end = stripped.rfind(")")
    if paren_start != -1 and paren_end != -1 and paren_end > paren_start:
        params_str = stripped[paren_start + 1:paren_end]
        if params_str:
            try:
                params = json.loads(params_str)
            except json.JSONDecodeError:
                params = {"raw": params_str}
    
    return (action_type, params)


def get_action_duration(action_type: str, params: Optional[Dict] = None) -> int:
    """
    Get the duration of an action in ticks.
    
    Args:
        action_type: The type of action.
        params: Optional parameters that may affect duration.
    
    Returns:
        Duration in ticks.
    """
    base_duration = ACTION_DURATIONS.get(action_type.upper(), 1)
    
    # Allow custom duration in params
    if params and "duration" in params:
        return int(params["duration"])
    
    return base_duration


def get_action_effects(action_type: str, params: Optional[Dict] = None) -> Dict[str, float]:
    """
    Get the physio effects of an action.
    
    Args:
        action_type: The type of action.
        params: Optional parameters that may affect effects.
    
    Returns:
        Dictionary of physio effects.
    """
    return ACTION_COSTS.get(action_type.upper(), {}).copy()


def execute_work_action(agent: Any, world: Any, params: Dict = None) -> ActionResult:
    """
    Execute WORK action for an agent.
    
    Args:
        agent: The agent performing the action.
        world: The world context.
        params: Action parameters (task, duration).
    
    Returns:
        ActionResult with success status and effects.
    """
    params = params or {}
    
    # Validate that agent is at a work-capable location
    if agent.place not in world.places:
        return ActionResult(
            success=False,
            message=f"Agent is not at a valid place: {agent.place}"
        )
    
    place = world.places[agent.place]
    
    # Check for work capability - use agent's own validation method if available
    if hasattr(agent, '_work_allowed_here'):
        if not agent._work_allowed_here(world):
            return ActionResult(
                success=False,
                message=f"Cannot work at {agent.place}. Job '{agent.persona.job}' does not match this location"
            )
    elif "work" not in place.capabilities:
        return ActionResult(
            success=False,
            message=f"Cannot work at {agent.place}. Location lacks work capability"
        )
    
    duration = get_action_duration("WORK", params)
    effects = get_action_effects("WORK", params)
    
    # Calculate reward
    reward = params.get("reward", 10)
    
    return ActionResult(
        success=True,
        message=f"Working at {agent.place}",
        duration=duration,
        effects=effects
    )


def execute_say_action(agent: Any, world: Any, params: Dict = None) -> ActionResult:
    """
    Execute SAY action for an agent.
    
    Args:
        agent: The agent performing the action.
        world: The world context.
        params: Action parameters (text, to).
    
    Returns:
        ActionResult with success status.
    """
    params = params or {}
    text = params.get("text", "")
    target = params.get("to", None)
    
    if not text:
        return ActionResult(
            success=False,
            message="No text provided for SAY action"
        )
    
    # Broadcast to current location
    message = {
        "actor": agent.persona.name,
        "action": "SAY",
        "text": text,
        "to": target
    }
    
    return ActionResult(
        success=True,
        message=f"Said: {text}",
        duration=get_action_duration("SAY"),
        effects=get_action_effects("SAY")
    )


def execute_interact_action(agent: Any, world: Any, params: Dict = None) -> ActionResult:
    """
    Execute INTERACT action for an agent.
    
    Args:
        agent: The agent performing the action.
        world: The world context.
        params: Action parameters (target, action_type).
    
    Returns:
        ActionResult with success status.
    """
    params = params or {}
    target = params.get("target", "")
    action_type = params.get("action_type", "observe")
    
    if not target:
        return ActionResult(
            success=False,
            message="No target provided for INTERACT action"
        )
    
    # Check if target is in the same location
    if agent.place in world.places:
        place = world.places[agent.place]
        agents_here = [a.persona.name for a in place.agents_present]
        
        # Target could be an agent or an object
        if target not in agents_here:
            # Check if it's an object/item in the place by ID or name
            items_here = place.get_items()  # Returns dict of item_id -> quantity
            # Check by item ID
            if target not in items_here:
                # Also check by item name for user-friendly matching
                item_names = []
                for stack in place.inventory.stacks:
                    item_names.append(stack.item.name.lower())
                    item_names.append(stack.item.id.lower())
                if target.lower() not in item_names:
                    return ActionResult(
                        success=False,
                        message=f"Target '{target}' not found at {agent.place}"
                    )
    
    return ActionResult(
        success=True,
        message=f"Interacting with {target}: {action_type}",
        duration=get_action_duration("INTERACT"),
        effects=get_action_effects("INTERACT")
    )
