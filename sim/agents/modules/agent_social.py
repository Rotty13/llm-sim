"""
AgentSocial module for managing agent social interactions and networks.
Handles social graph, connections, and interaction history.
"""

class AgentSocial:
    def __init__(self):
        self.connections = {}
        self.interactions = []

    def add_connection(self, agent_id, connection_type):
        self.connections[agent_id] = connection_type

    def get_connection(self, agent_id):
        return self.connections.get(agent_id)

    def log_interaction(self, agent_id, interaction):
        self.interactions.append((agent_id, interaction))

    def get_interactions(self):
        return self.interactions.copy()

    def all_connections(self):
        return self.connections.copy()
