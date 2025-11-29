from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..agents.agents import Agent
    from .world import World

def set_agent_location(world: 'World', agent: 'Agent', place_name: str):
    """Set the location of an agent in the world."""
    if place_name not in world.places:
        raise ValueError(f"Place '{place_name}' does not exist in the world.")

    # Remove agent from current place
    current_place_name = world.get_agent_location(agent.persona.name)
    if current_place_name and current_place_name in world.places:
        current_place = world.places[current_place_name]
        if hasattr(current_place, 'agents_present') and agent in current_place.agents_present:
            current_place.agents.remove(agent)

    # Add agent to the new place
    world.places[place_name].add_agent(agent)
    world.agent_locations[agent.persona.name] = place_name

def get_agent_location(world: 'World', agent_name: str) -> str:
    """Get the location of an agent by name."""
    return world.agent_locations.get(agent_name)