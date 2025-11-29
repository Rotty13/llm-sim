from typing import Protocol, Dict, Any

class WorldInterface(Protocol):
    def get_agent_location(self, agent_name: str) -> str:
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
        pass

    @property
    def places(self) -> Dict[str, Any]:
        """Dictionary of places in the world."""
        pass