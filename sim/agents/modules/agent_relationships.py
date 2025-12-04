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

    def set_relationship(self, other: str, familiarity: float = 0.5, trust: float = 0.5, affinity: float = 0.0, rivalry: float = 0.0, influence: float = 0.0):
        self.relationships[other] = {
            "familiarity": familiarity,
            "trust": trust,
            "affinity": affinity,
            "rivalry": rivalry,
            "influence": influence
        }

    def get_relationship(self, other: str) -> Dict[str, float]:
        rel = self.relationships.get(other)
        if isinstance(rel, dict):
            # Ensure all keys exist
            for k in ["familiarity", "trust", "affinity", "rivalry", "influence"]:
                rel.setdefault(k, 0.0)
            return rel
        return {"familiarity": 0.0, "trust": 0.0, "affinity": 0.0, "rivalry": 0.0, "influence": 0.0}

    def update_familiarity(self, other: str, delta: float):
        rel = self.relationships.get(other)
        if not isinstance(rel, dict):
            rel = {"familiarity": 0.0, "trust": 0.0, "affinity": 0.0, "rivalry": 0.0, "influence": 0.0}
        rel["familiarity"] = max(0.0, min(1.0, rel["familiarity"] + delta))
        self.relationships[other] = rel

    def update_trust(self, other: str, delta: float):
        rel = self.relationships.get(other)
        if not isinstance(rel, dict):
            rel = {"familiarity": 0.0, "trust": 0.0, "affinity": 0.0, "rivalry": 0.0, "influence": 0.0}
        rel["trust"] = max(0.0, min(1.0, rel["trust"] + delta))
        self.relationships[other] = rel

    def update_relationship(self, other: str, delta: float, field: str = "familiarity"):
        rel = self.relationships.get(other)
        if not isinstance(rel, dict):
            rel = {"familiarity": 0.0, "trust": 0.0, "affinity": 0.0, "rivalry": 0.0, "influence": 0.0}
        if field in rel:
            rel[field] = max(0.0, min(1.0, rel[field] + delta))
        self.relationships[other] = rel

    def update_affinity(self, other: str, delta: float):
        self.update_relationship(other, delta, field="affinity")

    def update_rivalry(self, other: str, delta: float):
        self.update_relationship(other, delta, field="rivalry")

    def update_influence(self, other: str, delta: float):
        self.update_relationship(other, delta, field="influence")
