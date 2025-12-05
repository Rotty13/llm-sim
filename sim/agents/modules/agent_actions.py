"""
AgentActions module for managing agent actions and action history.
Handles action execution, logging, and queries.
"""

class AgentActions:
    def perform_social_action(self, agent, other_agent=None, world=None, action_type="SAY", context=None):
        """
        Perform a social action (SAY/INTERACT), generate a topic, and log the interaction.
        """
        # Generate topic using AgentSocial static method
        topic = None
        if agent.social:
            topic = agent.social.generate_topic(agent, context)
            # Log interaction for both agents if possible
            agent.social.log_interaction(
                other_agent.persona.name if other_agent else None,
                action_type,
                topic
            )
            if other_agent and hasattr(other_agent, 'social') and other_agent.social:
                other_agent.social.log_interaction(
                    agent.persona.name,
                    action_type,
                    topic
                )
        return topic
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
        Handles all canonical actions and logs them with details.
        """
        import sim.actions.actions as actions_mod
        action = decision.get("action", "").upper()
        params = decision.get("params", {})
        result = None

        # Canonical action routing
        if action == "MOVE" and agent.movement_controller:
            destination = params.get("to")
            if destination:
                agent.movement_controller.move_to(agent, world, destination)
                result = {"success": True, "message": f"Moved to {destination}"}
            else:
                result = {"success": False, "message": "No destination provided"}
        elif action == "SAY":
            result_obj = actions_mod.execute_say_action(agent, world, params)
            result = result_obj.__dict__
        elif action == "INTERACT":
            result_obj = actions_mod.execute_interact_action(agent, world, params)
            result = result_obj.__dict__
        elif action == "WORK":
            result_obj = actions_mod.execute_work_action(agent, world, params)
            result = result_obj.__dict__
        elif action == "TRADE":
            result_obj = actions_mod.execute_trade_action(agent, world, params)
            result = result_obj.__dict__
        elif action == "BUY" or action == "SELL":
            # execute_buy_action in actions.py implements both BUY and SELL logic
            result_obj = actions_mod.execute_buy_action(agent, world, params)
            result = result_obj.__dict__
        # Generic actions (THINK, PLAN, SLEEP, EAT, CONTINUE, RELAX, EXPLORE, WASH, REST, USE_BATHROOM)
        elif action in actions_mod.ACTION_DURATIONS:
            # Simulate effects and duration
            duration = actions_mod.get_action_duration(action, params)
            effects = actions_mod.get_action_effects(action, params)
            result = {
                "success": True,
                "message": f"Performed {action}",
                "duration": duration,
                "effects": effects
            }
        else:
            result = {"success": False, "message": f"Unknown action: {action}"}

        # Record action history with details
        self.action_history.append({
            "agent": agent.persona.name,
            "action": action,
            "params": params,
            "tick": tick,
            "result": result
        })

        # Log the action to world metrics with details
        if hasattr(world, "log_agent_action"):
            # Pass details if supported (agent_name, action, details)
            if hasattr(world, "metrics") and hasattr(world.metrics, "log_agent_action"):
                world.metrics.log_agent_action(agent.persona.name, action, {"params": params, "result": result})
            else:
                world.log_agent_action(agent, action)
        return result

    def perform_action(self, *args, **kwargs):
        """Alias for execute method for compatibility with tests."""
        return self.execute(*args, **kwargs)

    def get_last_action(self):
        if self.action_history:
            return self.action_history[-1]
        return None

    def all_actions(self):
        return self.action_history.copy()
