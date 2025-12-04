"""
AgentObservation module for managing agent observations and diary logic.
Handles adding observations and diary entries with similarity checks.
"""
from difflib import SequenceMatcher

class AgentObservation:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self._last_diary_tick = -999
        self._last_diary = ""

    def add_observation(self, text):
        if self.memory_manager:
            self.memory_manager.add_observation(text)

    def maybe_write_diary(self, text, tick):
        if not text:
            return
        if (tick - self._last_diary_tick) < 6:
            return
        if self.memory_manager and hasattr(self.memory_manager, '_norm_text'):
            sim = SequenceMatcher(None, self.memory_manager._norm_text(self._last_diary), self.memory_manager._norm_text(text)).ratio()
            if sim < 0.93:
                self.memory_manager.write_memory(type('MemoryItem', (), {'t': tick, 'kind': 'autobio', 'text': text, 'importance': 0.6})())
                self._last_diary, self._last_diary_tick = text, tick
