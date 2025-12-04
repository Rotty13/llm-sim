"""
AgentActions module for managing agent actions and action history.
Handles action execution, logging, and queries.
"""

class AgentActions:
    def work_at_place(self, agent, place, world, tick):
        """Perform work at the current place, earning income and producing job-related items."""
        if agent.place != place:
            return False
        agent.update_income()
        # Example: produce job-related items
        job = getattr(agent.persona, 'job', None)
        if job == 'baker':
            # Add pastry to inventory
            if agent.inventory:
                from sim.inventory.inventory import ITEMS
                agent.inventory.add_item(ITEMS['pastry'], 1)
        elif job == 'artist':
            if agent.inventory:
                from sim.inventory.inventory import ITEMS
                agent.inventory.add_item(ITEMS['sketch'], 1)
        # Extend with more jobs as needed
        return True

    def buy_from_vendor(self, agent, vendor, item_id, qty=1):
        """Buy an item from a vendor and add to agent inventory."""
        # Example: vendor has a 'sell' method
        if hasattr(vendor, 'sell'):
            item = vendor.sell(item_id, qty)
            if item and agent.inventory:
                agent.inventory.add_item(item, qty)
                return True
        return False

    def sell_to_vendor(self, agent, vendor, item_id, qty=1):
        """Sell an item from agent inventory to a vendor."""
        if agent.inventory and agent.inventory.has_item(item_id):
            if hasattr(vendor, 'buy'):
                success = vendor.buy(item_id, qty)
                if success:
                    agent.inventory.remove_item(item_id, qty)
                    return True
        return False

    def interact_with_inventory(self, agent, inventory, item_id, qty=1):
        """Transfer item between agent and another inventory."""
        if agent.inventory and agent.inventory.has_item(item_id):
            agent.inventory.remove_item(item_id, qty)
            if hasattr(inventory, 'add_item'):
                inventory.add_item(item_id, qty)
            return True
        return False

    def interact_with_place(self, agent, place, item_id, qty=1):
        """Deposit or withdraw items at a place."""
        # Example: place has inventory
        if hasattr(place, 'inventory') and agent.inventory:
            # Deposit item
            if agent.inventory.has_item(item_id):
                agent.inventory.remove_item(item_id, qty)
                place.inventory.add_item(item_id, qty)
                return True
            # Withdraw item
            elif hasattr(place.inventory, 'has_item') and place.inventory.has_item(item_id):
                place.inventory.remove_item(item_id, qty)
                agent.inventory.add_item(item_id, qty)
                return True
        return False
    def get_life_stage_action_modifiers(self, agent):
        """Return action restrictions or enhancements based on life stage."""
        stage = getattr(agent.persona, 'life_stage', 'adult')
        # Example: restrict certain actions for infants/toddlers/elders
        restrictions = {
            'infant':    ['WORK', 'EXPLORE', 'SAY', 'CLEAN', 'INTERACT'],
            'toddler':   ['WORK', 'EXPLORE', 'SAY', 'CLEAN', 'INTERACT'],
            'child':     [],
            'teen':      [],
            'young adult': [],
            'adult':     [],
            'elder':     ['WORK'],
        }
        return restrictions.get(stage, [])

    def __init__(self):
        self.action_history = []

    def execute(self, agent, world, decision, tick):
        """
        Execute the given action for the agent in the simulation context.
        Accepts a decision dict as delegated from Agent.act.
        """
        action = decision.get("action", "")
        params = decision.get("params", {})
        if action == "MOVE" and agent.movement_controller:
            destination = params.get("to")
            if destination:
                agent.movement_controller.move_to(agent, world, destination)
        # Add more action handling as needed, e.g., EAT, SLEEP, etc.
        self.action_history.append({
            "agent": agent.persona.name,
            "action": action,
            "params": params,
            "tick": tick
        })
        return True

    def perform_action(self, *args, **kwargs):
        """Alias for execute method for compatibility with tests."""
        return self.execute(*args, **kwargs)

    def get_last_action(self):
        if self.action_history:
            return self.action_history[-1]
        return None

    def all_actions(self):
        return self.action_history.copy()
