"""
metrics.py

Simulation metrics and logging utilities for llm-sim.
Tracks agent actions, resource flows, and world events for analysis.
"""
from collections import defaultdict

class SimulationMetrics:
    def __init__(self):
        self.agent_actions = defaultdict(int)
        self.resource_flows = defaultdict(int)
        self.world_events = defaultdict(int)

    def log_agent_action(self, agent_name, action):
        self.agent_actions[(agent_name, action)] += 1

    def log_resource_flow(self, entity, item_id, qty):
        self.resource_flows[(entity, item_id)] += qty

    def log_world_event(self, event):
        self.world_events[event] += 1

    def summary(self):
        return {
            "agent_actions": dict(self.agent_actions),
            "resource_flows": dict(self.resource_flows),
            "world_events": dict(self.world_events)
        }
