"""
Handles all memory-related operations for an agent.

Classes:
    MemoryManager: Manages memory storage, recall, and observations.

Methods:
    add_observation(observation: str): Adds an observation to the memory store.
    write_memory(memory_item: MemoryItem): Writes a memory item to the memory store.
    recall_memories(query: str, k: int = 5): Recalls memories based on a query.
"""

from sim.memory.memory import MemoryStore, MemoryItem
import string

class MemoryManager:
    """
    Handles all memory-related operations for an agent.
    """
    def __init__(self):
        self.memory_store = MemoryStore()
        self.obs_list = []  # Maintain observations separately

    def add_observation(self, observation: str):
        """
        Add an observation to the observation list.
        """
        if observation and observation not in self.obs_list:
            self.obs_list.append(observation)
            if len(self.obs_list) > 20:
                self.obs_list.pop(0)

    def write_memory(self, memory_item: MemoryItem):
        """
        Write a memory item to the memory store.
        """
        self.memory_store.write(memory_item)

    def recall_memories(self, query: str, k: int = 5):
        """
        Recall memories based on a query.
        """
        return self.memory_store.recall(query, k=k)

    def _norm_text(self, s: str) -> str:
        """
        Normalize text by converting to lowercase and removing punctuation.
        """
        return "".join(ch for ch in (s or "").lower().strip() if ch not in string.punctuation)