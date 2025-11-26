"""
Handles decision-making logic for an agent.

Classes:
    DecisionController: Centralizes decision-making logic.

Methods:
    decide(agent: Any, world: World, obs_text: str, tick: int, start_dt):
        Makes a decision based on the agent's state and observations.
"""

from typing import Dict, Any
from sim.world.world import World

class DecisionController:
    """
    Handles decision-making logic for an agent.
    """
    def decide(self, agent: Any, world: World, obs_text: str, tick: int, start_dt) -> Dict[str, Any]:
        """
        Make a decision based on the agent's state and observations.
        """
        # Enhanced rule-based decision
        if agent.physio.hunger > 0.8:
            if "food" in world.places[agent.place].capabilities:
                return {"action": "EAT", "params": {"location": agent.place}}
            else:
                return {"action": "MOVE", "params": {"to": "nearest_food"}}
        elif agent.physio.energy < 0.3:
            if agent.place == "home":
                return {"action": "SLEEP"}
            else:
                return {"action": "MOVE", "params": {"to": "home"}}

        # Example probabilistic decision
        import random
        if random.random() < 0.5:
            return {"action": "EXPLORE", "params": {"area": "nearby"}}
        else:
            return {"action": "RELAX", "params": {"duration": 30}}