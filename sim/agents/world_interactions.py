from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world.world import World
    from .agents import Agent

def deposit_item_to_place(agent: 'Agent', world: 'World', item_id: str, qty: int = 1) -> bool:
    """
    Delegate depositing items to the InventoryHandler.
    Updates busy_until to reflect the time taken for the action.
    """
    place_name = world.get_agent_location(agent.persona.name)
    if not place_name:
        return False

    place = world.places.get(place_name)
    if not place:
        return False

    success = agent.inventory_handler.deposit_item_to_place(agent, place, item_id, qty)
    if success:
        agent.busy_until += 5  # Example: Depositing takes 5 ticks
    return success

def withdraw_item_from_place(agent: 'Agent', world: 'World', item_id: str, qty: int = 1) -> bool:
    """
    Delegate withdrawing items to the InventoryHandler.
    Updates busy_until to reflect the time taken for the action.
    """
    place_name = world.get_agent_location(agent.persona.name)
    if not place_name:
        return False

    place = world.places.get(place_name)
    if not place:
        return False

    success = agent.inventory_handler.withdraw_item_from_place(agent, place, item_id, qty)
    if success:
        agent.busy_until += 5  # Example: Withdrawing takes 5 ticks
    return success