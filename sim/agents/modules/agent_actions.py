"""
AgentActions module for managing agent actions and action history.
Handles action execution, logging, and queries.
"""

class AgentActions:
    def __init__(self):
        self.action_history = []

    def perform_action(self, action):
        self.action_history.append(action)
        # Placeholder for action execution logic
        return f"Action performed: {action}"

    def get_last_action(self):
        if self.action_history:
            return self.action_history[-1]
        return None

    def all_actions(self):
        return self.action_history.copy()
