"""
agent_relationships.py

Handles agent relationship management for llm-sim agents.
Includes familiarity and trust logic, and relationship update methods.
"""
from typing import Dict, Any

class AgentRelationships:
    def serialize(self) -> dict:
        """
        Return a serializable copy of relationships.
        """
        return {k: v.copy() for k, v in self.relationships.items()}

    def load(self, data: dict):
        """
        Load relationships from a dict.
        """
        if isinstance(data, dict):
            self.relationships = {k: v.copy() for k, v in data.items()}
    def __init__(self):
        self.relationships: Dict[str, Dict[str, Any]] = {}

    def __contains__(self, key):
        return key in self.relationships

    def __getitem__(self, key):
        rel = self.relationships.get(key)
        if isinstance(rel, dict):
            return rel.get("familiarity", 0.0)
        return 0.0

    def set_relationship(self, other: str, familiarity: float = 0.5, trust: float = 0.5, affinity: float = 0.0, rivalry: float = 0.0, influence: float = 0.0, rel_type: str = "acquaintance"):
        """
        Set or update a relationship with another agent, including type.
        rel_type: e.g., 'friend', 'family', 'colleague', 'rival', 'acquaintance'
        """
        self.relationships[other] = {
            "familiarity": familiarity,
            "trust": trust,
            "affinity": affinity,
            "rivalry": rivalry,
            "influence": influence,
            "type": rel_type  # type is str, others are float
        }

    def get_relationship(self, other: str) -> Dict[str, Any]:
        rel = self.relationships.get(other)
        if isinstance(rel, dict):
            # Ensure all keys exist
            for k in ["familiarity", "trust", "affinity", "rivalry", "influence"]:
                rel.setdefault(k, 0.0)
                if "type" not in rel or not isinstance(rel["type"], str):
                    rel["type"] = "acquaintance"
            return rel
        return {"familiarity": 0.0, "trust": 0.0, "affinity": 0.0, "rivalry": 0.0, "influence": 0.0, "type": "acquaintance"}
    def get_relationship_type(self, other: str) -> str:
        rel = self.relationships.get(other)
        if isinstance(rel, dict):
              t = rel.get("type", "acquaintance")
              return t if isinstance(t, str) else "acquaintance"
        return "acquaintance"

    def set_relationship_type(self, other: str, rel_type: str):
        rel = self.relationships.get(other)
        if isinstance(rel, dict):
            rel["type"] = rel_type
            self.relationships[other] = rel

    def relationship_effect_on_decision(self, other: str) -> float:
        """
        Returns a modifier for decision logic based on relationship type and strength.
        Example: friends increase likelihood to help, rivals decrease it.
        """
        rel = self.get_relationship(other)
        rel_type = rel.get("type", "acquaintance")
        affinity = rel.get("affinity", 0.0)
        rivalry = rel.get("rivalry", 0.0)
        trust = rel.get("trust", 0.0)
        # Example logic:
        if rel_type == "friend":
            return affinity + trust
        elif rel_type == "family":
            return affinity + trust + 0.2
        elif rel_type == "colleague":
            return affinity + trust * 0.5
        elif rel_type == "rival":
            return -rivalry
        return affinity + trust * 0.2 - rivalry * 0.2

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
