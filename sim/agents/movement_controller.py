"""
Handles movement and location updates for an agent.

Classes:
    MovementController: Manages agent movement and location updates.

Methods:
    move_to(agent: Any, world: World, destination: str):
        Moves the agent to a new location if valid.
"""

from sim.world.world import World
from typing import Any

class MovementController:
    """
    Handles movement and location updates for an agent.
    """
    def move_to(self, agent: Any, world: World, destination: str) -> bool:
        """
        Move the agent to a new location if valid.
        """
        if destination in world.places and destination != agent.place:
            agent.place = destination
            world.set_agent_location(agent, destination)
            return True
        return False