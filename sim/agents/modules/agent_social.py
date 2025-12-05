import sim.utils.metrics
import logging  # Use standard logging for now; TODO: inject world-specific logger
import random
"""
AgentSocial module for managing agent social interactions and networks.
Handles social graph, connections, and interaction history.

Features:
- Social graph management (connections, affinity, rivalry, influence)
- Interaction and topic history tracking
- Context-aware topic generation
- Logging and metrics integration
- API for querying recent topics and interactions
"""

class AgentSocial:
    def __init__(self):
        self.connections = {}
        self.interactions = []  # List of (agent_id, interaction, topic)
        self.topic_history = []  # List of (agent_id, topic)

    def get_social_influence_modifier(self, topic=None):
        """
        Return a modifier for a given topic based on recent interactions and influence scores.
        Increases modifier if topic is popular or discussed by influential agents.
        """
        # Count frequency of topic in recent interactions
        recent_topics = [t for aid, t in self.topic_history[-20:] if t]
        topic_count = recent_topics.count(topic) if topic else 0
        # Influence: sum influence scores for agents who discussed the topic
        influence_sum = 0.0
        if topic:
            for aid, t in self.topic_history[-20:]:
                if t == topic and aid in self.connections:
                    influence_sum += self.connections[aid].get('influence', 0.0)
        # Simple modifier: base + topic frequency + influence
        modifier = 0.0
        modifier += 0.1 * topic_count
        modifier += 0.2 * influence_sum
        return modifier

    def generate_topic(self, agent=None, context=None):
        """
        Generate a conversation topic based on static pool and context.
        agent: the agent initiating conversation (optional)
        context: dict with keys like 'event', 'location', etc. (optional)
        """
        # Static topic pool
        topics = ['weather', 'work', 'food', 'hobbies', 'news', 'family', 'health', 'sports', 'local_places']
        # Contextual topics
        if context:
            if 'event' in context and context['event']:
                topics.append(context['event'])
            if 'location' in context and context['location']:
                topics.append(f"about_{context['location']}")
        # Agent trait-based topics (example: extraversion prefers social topics)
        if agent and hasattr(agent, 'persona'):
            traits = getattr(agent.persona, 'traits', {})
            if traits.get('extraversion', 0) > 0.7:
                topics.append('social_life')
            if traits.get('openness', 0) > 0.7:
                topics.append('ideas')
        # Pick a topic
        return random.choice(topics)

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
        """Log an interaction with optional topic, record to sim_logger, and update metrics."""
        self.interactions.append((agent_id, interaction, topic))
        if topic:
            self.topic_history.append((agent_id, topic))
        logging.getLogger("llm-sim").info(
            f"AgentSocial interaction: agent_id={agent_id}, interaction={interaction}, topic={topic}",
            extra={"agent_id": agent_id, "interaction": interaction, "topic": topic}
        )
        sim.utils.metrics.metrics.log_agent_action(agent_id, interaction, details={"topic": topic})

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
