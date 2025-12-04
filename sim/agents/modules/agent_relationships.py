"""
agent_relationships.py

Handles agent relationship management for llm-sim agents.
Includes familiarity and trust logic, and relationship update methods.
"""
from typing import Dict

class AgentRelationships:
    def __init__(self):
        self.relationships: Dict[str, Dict[str, float]] = {}

    def __contains__(self, key):
        return key in self.relationships

    def __getitem__(self, key):
        rel = self.relationships.get(key)
        if isinstance(rel, dict):
            return rel.get("familiarity", 0.0)
        return 0.0

    def set_relationship(self, other: str, familiarity: float = 0.5, trust: float = 0.5):
        self.relationships[other] = {
            "familiarity": familiarity,
            "trust": trust
        }

    def get_relationship(self, other: str) -> Dict[str, float]:
        rel = self.relationships.get(other)
        if isinstance(rel, dict):
            return rel
        return {"familiarity": 0.0, "trust": 0.0}

    def update_familiarity(self, other: str, delta: float):
        rel = self.relationships.get(other)
        if not isinstance(rel, dict):
            rel = {"familiarity": 0.0, "trust": 0.0}
        rel["familiarity"] = max(0.0, min(1.0, rel["familiarity"] + delta))
        self.relationships[other] = rel

    def update_trust(self, other: str, delta: float):
        rel = self.relationships.get(other)
        if not isinstance(rel, dict):
            rel = {"familiarity": 0.0, "trust": 0.0}
        rel["trust"] = max(0.0, min(1.0, rel["trust"] + delta))
        self.relationships[other] = rel

    def update_relationship(self, other: str, delta: float):
        rel = self.relationships.get(other)
        if not isinstance(rel, dict):
            rel = {"familiarity": 0.0, "trust": 0.0}
        rel["familiarity"] = max(0.0, min(1.0, rel["familiarity"] + delta))
        self.relationships[other] = rel
