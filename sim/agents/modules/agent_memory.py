"""
AgentMemory module for managing agent episodic and semantic memories.
Handles memory storage, retrieval, and updates.
"""

class AgentMemory:
    def __init__(self):
        self.episodic = []
        self.semantic = {}

    def add_episodic(self, event):
        self.episodic.append(event)

    def add_semantic(self, key, value):
        self.semantic[key] = value

    def get_episodic(self):
        return self.episodic.copy()

    def get_semantic(self, key):
        return self.semantic.get(key)

    def all_semantic(self):
        return self.semantic.copy()

    def serialize(self):
        """Return a serializable dict of episodic and semantic memory."""
        return {
            "episodic": self.episodic.copy(),
            "semantic": self.semantic.copy()
        }

    def load(self, data):
        """Load episodic and semantic memory from a dict."""
        if isinstance(data, dict):
            self.episodic = data.get("episodic", []).copy()
            self.semantic = data.get("semantic", {}).copy()
