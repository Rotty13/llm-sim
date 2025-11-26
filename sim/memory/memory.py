"""
memory.py

Defines MemoryItem and MemoryStore for agent episodic and semantic memory, including embedding-based recall and recency decay logic.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import math

from sim.llm import llm_ollama
from sim.utils.utils import cosine, TICK_MINUTES

llm=llm_ollama.LLM()

RECENCY_DECAY = 0.85  # per hour

@dataclass
class MemoryItem:
    t: int
    kind: str           # 'episodic'|'semantic'|'autobio'|'tom'
    text: str
    importance: float = 0.5
    vec: Optional[List[float]] = None

    def __init__(self, t, kind, text, importance, vec=None):
        self.t = t
        self.kind = kind
        self.text = text
        self.importance = importance
        self.vec = vec if vec is not None else []

def _cos(u: List[float], v: List[float]) -> float:
    if not u or not v or len(u) != len(v): return 0.0
    su = sum(x*x for x in u); sv = sum(y*y for y in v)
    if su == 0 or sv == 0: return 0.0
    dot = sum(x*y for x, y in zip(u, v))
    return dot / math.sqrt(su * sv)

@dataclass
class MemoryStore:
    items: List[MemoryItem] = field(default_factory=list)
    _single_word_cache: dict = field(default_factory=dict, init=False, repr=False)

    def write(self, item: MemoryItem):
        # Normalize text to lowercase for embedding and caching
        item.text = item.text.lower()
        try:
            item.vec = llm.embed(item.text)
        except Exception:
            item.vec = []
        self.items.append(item)
        print(f"DEBUG: Memory written: {item.text}, vec: {item.vec}")

    def recall(self, q: str, k: int = 5) -> List[MemoryItem]:
        if not self.items:
            print("DEBUG: No items in memory.")
            return []
        # Normalize query to lowercase
        q_norm = q.lower()
        try:
            qv = llm.embed(q_norm)
        except Exception:
            qv = []
        print(f"DEBUG: Query vector: {qv}")
        latest_t = max(m.t for m in self.items) if self.items else 0
        scored = []
        for m in self.items:
            sim = _cos(qv, m.vec or [0] * len(qv))
            hrs = ((latest_t - m.t) * TICK_MINUTES) / 60.0
            rec = RECENCY_DECAY ** hrs
            score = 0.6 * sim + 0.3 * rec + 0.1 * m.importance
            scored.append((score, m))
            print(f"DEBUG: Memory: {m.text}, Score: {score}")
        scored.sort(key=lambda x: x[0], reverse=True)
        result = [m for _, m in scored[:k]]
        print(f"DEBUG: Final recalled items: {[m.text for m in result]}")
        return result

    def compress_nightly(self):
        """Sketch: keep top-N semantics and prune very old low-importance episodics."""
        keep = []
        for m in self.items:
            if m.kind == "semantic" or (m.importance >= 0.7):
                keep.append(m)
        # retain recent 200 memories
        self.items = (self.items[-200:] + keep)[-300:]
