"""
AgentSocial module for managing agent social interactions and networks.
Handles social graph, connections, and interaction history.
"""

class AgentSocial:
    def __init__(self):
        self.connections = {}
        self.interactions = []  # List of (agent_id, interaction, topic)
        self.topic_history = []  # List of (agent_id, topic)

    def update_affinity(self, agent_id, delta):
        """Update affinity score for a connection."""
        if agent_id not in self.connections:
            self.connections[agent_id] = {}
        conn = self.connections[agent_id]
        conn['affinity'] = max(0.0, min(1.0, conn.get('affinity', 0.0) + delta))
        self.connections[agent_id] = conn

    def update_rivalry(self, agent_id, delta):
        """Update rivalry score for a connection."""
        if agent_id not in self.connections:
            self.connections[agent_id] = {}
        conn = self.connections[agent_id]
        conn['rivalry'] = max(0.0, min(1.0, conn.get('rivalry', 0.0) + delta))
        self.connections[agent_id] = conn

    def update_influence(self, agent_id, delta):
        """Update influence score for a connection."""
        if agent_id not in self.connections:
            self.connections[agent_id] = {}
        conn = self.connections[agent_id]
        conn['influence'] = max(0.0, min(1.0, conn.get('influence', 0.0) + delta))
        self.connections[agent_id] = conn

    def add_connection(self, agent_id, connection_type):
        self.connections[agent_id] = {
            "type": connection_type,
            "affinity": 0.0,
            "rivalry": 0.0,
            "influence": 0.0
        }

    def get_connection(self, agent_id):
        return self.connections.get(agent_id)

    def log_interaction(self, agent_id, interaction, topic=None):
        """Log an interaction with optional topic."""
        self.interactions.append((agent_id, interaction, topic))
        if topic:
            self.topic_history.append((agent_id, topic))
    def get_recent_topics(self, agent_id=None, limit=10):
        """Return recent topics overall or for a specific agent."""
        if agent_id:
            topics = [topic for aid, topic in reversed(self.topic_history) if aid == agent_id and topic]
        else:
            topics = [topic for aid, topic in reversed(self.topic_history) if topic]
        return topics[:limit]

    def get_interactions(self):
        return self.interactions.copy()

    def all_connections(self):
        return self.connections.copy()
