"""
world_interface.py

Defines WorldInterface protocol for world simulation modules in llm-sim.
Specifies required methods and properties for agent location, action logging, resource flow, and event logging.

Key Methods:
- get_agent_location: Retrieve agent location by name.
- log_agent_action: Log agent actions in simulation metrics.
- log_resource_flow: Log resource movements.
- log_world_event: Log world events.

Key Properties:
- _agents: List of agents in the world.
- places: Dictionary of places in the world.

LLM Usage:
- None directly; interface may be implemented by modules that interact with LLMs.

CLI Arguments:
- None directly; interface is used by simulation modules and scripts.
"""

from typing import Protocol, Dict, Any, Optional

class WorldInterface(Protocol):
    def get_agent_location(self, agent_name: str) -> Optional[str]:
        """Get the location of an agent by name."""
        pass

    def log_agent_action(self, agent: Any, action: str):
        """Log an agent's action in the simulation metrics."""
        pass

    def log_resource_flow(self, entity: str, item_id: str, qty: int):
        """Log a resource flow in the simulation metrics."""
        pass

    def log_world_event(self, event: str):
        """Log a world event in the simulation metrics."""
        pass

    @property
    def _agents(self) -> list:
        """List of agents in the world."""
        ...

    @property
    def places(self) -> Dict[str, Any]:
        """Dictionary of places in the world."""
        ...