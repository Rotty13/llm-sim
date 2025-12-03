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
    - WASH: Agent washes to restore hygiene
    - REST: Agent rests to restore comfort
    - USE_BATHROOM: Agent uses bathroom to relieve bladder
"""
from __future__ import annotations
import json
import re
from typing import Any, Dict, Optional
from dataclasses import dataclass

ACTION_RE = re.compile(r'^(SAY|MOVE|INTERACT|THINK|PLAN|SLEEP|EAT|WORK|CONTINUE|RELAX|EXPLORE|BUY|SELL|TRADE|WASH|REST|USE_BATHROOM)(\((.*)\))?$')

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
    "TRADE": 2,  # Agent-to-agent trade
    "WASH": 4,   # 20 minutes
    "REST": 6,   # 30 minutes
    "USE_BATHROOM": 2, # 10 minutes
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
    "TRADE": {"energy": -0.02, "stress": 0.01},
    "WASH": {"hygiene": 0.8, "energy": -0.02},
    "REST": {"comfort": 0.7, "energy": 0.05, "stress": -0.1},
    "USE_BATHROOM": {"bladder": 1.0, "energy": -0.01},
}
def execute_trade_action(agent: Any, world: Any, params: Dict = None) -> ActionResult:
    """
    Execute TRADE action for agent-to-agent trading.
    Args:
        agent: The agent initiating the trade.
        world: The world context.
        params: Dict with keys: 'partner' (agent name), 'give' (dict: item, qty), 'receive' (dict: item, qty)
    Returns:
        ActionResult with success status and effects.
    """
    params = params or {}
    partner_name = params.get("partner")
    give = params.get("give", {})
    receive = params.get("receive", {})
    if not partner_name or not give or not receive:
        return ActionResult(False, "Invalid TRADE parameters.")
    # Find partner agent in world
    partner = None
    for a in getattr(world, '_agents', []):
        if getattr(a.persona, 'name', None) == partner_name:
            partner = a
            break
    if not partner:
        return ActionResult(False, f"Trade partner '{partner_name}' not found.")
    # Both agents must be in the same place
    if getattr(agent, 'place', None) != getattr(partner, 'place', None):
        return ActionResult(False, f"Both agents must be in the same place to trade.")
    # Validate agent has items to give
    give_item = give.get("item")
    give_qty = give.get("qty", 1)
    if not agent.inventory.has(give_item, give_qty):
        return ActionResult(False, f"You do not have enough {give_item} to trade.")
    # Validate partner has items to give
    receive_item = receive.get("item")
    receive_qty = receive.get("qty", 1)
    if not partner.inventory.has(receive_item, receive_qty):
        return ActionResult(False, f"Partner does not have enough {receive_item} to trade.")
    # Perform trade
    agent.inventory.remove(give_item, give_qty)
    partner.inventory.add(world.places[agent.place].inventory.ITEMS[give_item], give_qty)
    partner.inventory.remove(receive_item, receive_qty)
    agent.inventory.add(world.places[agent.place].inventory.ITEMS[receive_item], receive_qty)
    return ActionResult(
        True,
        f"Traded {give_qty} {give_item} for {receive_qty} {receive_item} with {partner_name}.",
        duration=get_action_duration("TRADE"),
        effects=get_action_effects("TRADE")
    )


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


def execute_buy_action(agent: Any, world: Any, params: Dict = None) -> ActionResult:
    def execute_sell_action(agent: Any, world: Any, params: Dict = None) -> ActionResult:
        """
        Execute SELL action for an agent.
        Args:
            agent: The agent performing the action.
            world: The world context.
            params: Action parameters (item, qty).
        Returns:
            ActionResult with success status and effects.
        """
        params = params or {}
        item_id = params.get("item")
        qty = params.get("qty", 1)
        place = world.places.get(agent.place)
        if not place or not getattr(place, "vendor", None):
            return ActionResult(
                success=False,
                message=f"No vendor at current location: {getattr(agent, 'place', None)}"
            )
        vendor = place.vendor
        if not item_id or not isinstance(qty, int) or qty <= 0:
            return ActionResult(
                success=False,
                message="Invalid item or quantity for SELL action"
            )
        if not agent.inventory.has(item_id, qty):
            return ActionResult(
                success=False,
                message=f"Not enough {item_id} to sell (need {qty})"
            )
        buyback_price = vendor.buyback.get(item_id, 0) * qty
        if buyback_price <= 0:
            return ActionResult(
                success=False,
                message=f"Vendor does not buy {item_id}"
            )
        # Attempt sale
        success = vendor.sell(item_id, qty, agent)
        if not success:
            return ActionResult(
                success=False,
                message=f"Sale failed for {qty} of {item_id}"
            )
        return ActionResult(
            success=True,
            message=f"Sold {qty} of {item_id} for {buyback_price}",
            duration=get_action_duration("SELL"),
            effects=get_action_effects("SELL")
        )
    """
    Execute BUY action for an agent.
    Args:
        agent: The agent performing the action.
        world: The world context.
        params: Action parameters (item, qty).
    Returns:
        ActionResult with success status and effects.
    """
    params = params or {}
    item_id = params.get("item")
    qty = params.get("qty", 1)
    place = world.places.get(agent.place)
    if not place or not getattr(place, "vendor", None):
        return ActionResult(
            success=False,
            message=f"No vendor at current location: {getattr(agent, 'place', None)}"
        )
    vendor = place.vendor
    if not item_id or not isinstance(qty, int) or qty <= 0:
        return ActionResult(
            success=False,
            message="Invalid item or quantity for BUY action"
        )
    if not vendor.has(item_id, qty):
        return ActionResult(
            success=False,
            message=f"Vendor does not have enough stock of {item_id}"
        )
    price = vendor.prices.get(item_id, 0) * qty
    if agent.money_balance < price:
        return ActionResult(
            success=False,
            message=f"Not enough money to buy {qty} of {item_id} (need {price})"
        )
    # Attempt purchase
    removed = agent.remove_money(price)
    if not removed:
        return ActionResult(
            success=False,
            message=f"Failed to deduct money for {qty} of {item_id}"
        )
    success = vendor.buy(item_id, qty, agent)
    if not success:
        # Refund money if vendor.buy fails
        agent.add_money(price)
        return ActionResult(
            success=False,
            message=f"Purchase failed for {qty} of {item_id}"
        )
    return ActionResult(
        success=True,
        message=f"Bought {qty} of {item_id} for {price}",
        duration=get_action_duration("BUY"),
        effects=get_action_effects("BUY")
    )
