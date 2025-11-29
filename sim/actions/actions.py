"""
actions.py

Defines the normalize_action function for converting action representations to a canonical DSL string. Used throughout the simulation for agent and system actions.
"""
from __future__ import annotations
import json, re
from typing import Any
from sim.inventory.inventory import ITEMS

ACTION_RE = re.compile(r'^(SAY|MOVE|INTERACT|THINK|PLAN|SLEEP|EAT|WORK|CONTINUE)(\((.*)\))?$')

def normalize_action(action: Any) -> str:
    """Accept dict or string, return canonical DSL string."""
    if isinstance(action, dict):
        atype = (action.get("type") or action.get("action") or "THINK").strip()
        payload = {k:v for k,v in action.items() if k not in ("type","action")}
        return f"{atype}({json.dumps(payload)})" if payload else f"{atype}()"
    if isinstance(action, str):
        s = action.strip()
        if s in ("SAY","MOVE","INTERACT","THINK","PLAN","SLEEP","EAT","WORK","CONTINUE"):
            return f"{s}()"
        m = ACTION_RE.match(s)
        #return f"{m.group(1)}{m.group(2) or '()'}" if m else 'THINK({"note":"nothing"})'
    return f'invalid action format: {action}'

def work_action(agent, place):
    """
    Implement the WORK action for an agent, with job-site validation and prerequisites.
    """
    if "work" in place.capabilities:
        reward = place.vendor.prices.get("work_reward", 10) if place.vendor else 10
        agent.physio.energy -= 0.1
        agent.inventory.add(ITEMS.get("money"), reward)
        return f"Agent {agent.persona.name} worked at {place.name} and earned {reward} units."
    return f"Agent {agent.persona.name} cannot work at {place.name}."

def say_action(agent, audience, message):
    """
    Implement the SAY action for an agent, targeting an audience.
    """
    for listener in audience:
        listener.add_observation({"speaker": agent.persona.name, "message": message})
    return f"Agent {agent.persona.name} said: '{message}'"

def interact_action(agent, target, interaction_type):
    """
    Implement the INTERACT action for object/agent interaction.
    """
    if hasattr(target, "interact_with_agent"):
        return target.interact_with_agent(agent, interaction_type)
    return f"Interaction failed: {agent.persona.name} could not interact with {target}."
