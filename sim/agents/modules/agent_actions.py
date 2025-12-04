"""
AgentActions module for managing agent actions and action history.
Handles action execution, logging, and queries.
"""

class AgentActions:
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
