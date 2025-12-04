"""
memory.py

Defines MemoryItem and MemoryStore for agent episodic and semantic memory, including embedding-based recall and recency decay logic.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import math


from sim.utils.utils import TICK_MINUTES
# from sim.llm import llm_ollama
# llm = llm_ollama.LLM()  # LLM/embedding logic is disabled for now

RECENCY_DECAY = 0.85  # per hour

@dataclass
class MemoryItem:
    t: int
    kind: str           # 'episodic'|'semantic'|'autobio'
    text: str
    importance: float = 0.5
    vec: Optional[List[float]] = None  # Unused for now; reserved for future embedding support

    def __init__(self, t, kind, text, importance, vec=None):
        self.t = t
        self.kind = kind
        self.text = text
        self.importance = importance
        # self.vec = vec if vec is not None else []  # Embedding logic disabled
        self.vec = None

# def _cos(u: List[float], v: List[float]) -> float:
#     if not u or not v or len(u) != len(v): return 0.0
#     su = sum(x*x for x in u); sv = sum(y*y for y in v)
#     if su == 0 or sv == 0: return 0.0
#     dot = sum(x*y for x, y in zip(u, v))
#     return dot / math.sqrt(su * sv)

@dataclass
class MemoryStore:
    """Store for agent memories with recall and compression capabilities."""
    items: List[MemoryItem] = field(default_factory=list)
    _single_word_cache: dict = field(default_factory=dict, init=False, repr=False)

    def apply_forgetting_curve(self, current_tick: int, decay_rate: float = 0.98, min_importance: float = 0.05):
        """
        Apply a forgetting curve to all memories, decaying importance over time.
        Memories with importance below min_importance are pruned.
        """
        for m in self.items:
            # Decay importance based on age (in ticks)
            age = max(0, current_tick - m.t)
            m.importance *= decay_rate ** (age / 24)  # decay per 24 ticks (2 hours)
        # Prune memories below threshold
        before = len(self.items)
        self.items = [m for m in self.items if m.importance >= min_importance]
        after = len(self.items)
        print(f"DEBUG: Forgetting curve applied. Pruned {before - after} memories.")

    def write(self, item: MemoryItem):
        # Normalize text to lowercase for consistency
        item.text = item.text.lower()
        # Rule-based importance calculation
        item.importance = self.calculate_importance(item)
        # Embedding logic disabled; keep for future use
        # try:
        #     item.vec = llm.embed(item.text)
        # except Exception:
        #     item.vec = []
        self.items.append(item)
        print(f"DEBUG: Memory written: {item.text}, importance: {item.importance}")

    def calculate_importance(self, item: MemoryItem, persona=None) -> float:
        """
        Rule-based importance calculation from context, plus personality trait adjustment:
        - High for emotional/urgent/goal-related words
        - Medium for social or novel events
        - Low for routine or repeated events
        - Personality traits boost importance for certain types of memories
        """
        high_keywords = ["urgent", "danger", "love", "hate", "goal", "success", "failure", "fear", "excited", "angry", "happy", "sad", "important", "critical"]
        medium_keywords = ["talked", "met", "new", "learned", "helped", "shared", "discussed", "explored", "found", "lost"]
        low_keywords = ["routine", "usual", "everyday", "normal", "boring", "repeated", "again"]
        text = item.text.lower()
        score = 0.5
        for word in high_keywords:
            if word in text:
                score += 0.4
        for word in medium_keywords:
            if word in text:
                score += 0.2
        for word in low_keywords:
            if word in text:
                score -= 0.2
        # Personality trait adjustment (if persona provided)
        if persona and hasattr(persona, 'traits'):
            traits = persona.traits
            if "sad" in text or "failure" in text:
                score += 0.2 * traits.get("neuroticism", 0.5)
            if "new" in text or "explore" in text:
                score += 0.2 * traits.get("openness", 0.5)
            if "friend" in text or "talk" in text:
                score += 0.2 * traits.get("extraversion", 0.5)
        # Clamp between 0.0 and 1.0
        score = max(0.0, min(1.0, score))
        # Optionally, boost importance for rare/unique events
        if not any(item.text == m.text for m in self.items):
            score += 0.1
        return max(0.0, min(1.0, score))

    def recall(self, q: str, k: int = 5, kind: str = None) -> List[MemoryItem]:
        """
        Recall memories matching a query and/or kind, ranked by keyword, recency, and importance.
        Args:
            q: Query string (optional, can be empty for kind-only search)
            k: Number of memories to return
            kind: Filter by memory kind (e.g., 'episodic', 'semantic', etc.)
        """
        if not self.items:
            print("DEBUG: No items in memory.")
            return []
        q_norm = q.lower() if q else ""
        latest_t = max(m.t for m in self.items) if self.items else 0
        filtered = self.items
        if kind:
            filtered = [m for m in filtered if m.kind == kind]
        scored = []
        for m in filtered:
            keyword_score = 1.0 if q_norm and q_norm in m.text else 0.0
            hrs = ((latest_t - m.t) * TICK_MINUTES) / 60.0
            rec = RECENCY_DECAY ** hrs
            score = 0.6 * keyword_score + 0.3 * rec + 0.1 * m.importance
            scored.append((score, m))
            print(f"DEBUG: Memory: {m.text}, Kind: {m.kind}, Score: {score}")
        scored.sort(key=lambda x: x[0], reverse=True)
        result = [m for _, m in scored[:k]]
        print(f"DEBUG: Final recalled items: {[m.text for m in result]}")
        return result

    def compress_nightly(self):
        """
        Consolidate episodic memories into semantic summaries:
        - Group similar episodics by keyword (simple heuristic)
        - Create a semantic summary for each group
        - Prune original episodics that were summarized
        - Retain all semantic and high-importance memories, and the most recent 200
        """
        from collections import defaultdict, Counter
        # 1. Group episodic memories by most frequent keyword (naive approach)
        episodics = [m for m in self.items if m.kind == "episodic"]
        groups = defaultdict(list)
        for m in episodics:
            # Use first non-trivial word as group key (improve as needed)
            words = [w for w in m.text.split() if len(w) > 3]
            key = words[0] if words else "misc"
            groups[key].append(m)
        # 2. For each group with >2 items, create a semantic summary
        new_semantics = []
        for key, group in groups.items():
            if len(group) > 2:
                # Make a summary string (simple join, could be improved)
                summary = f"Summary of {len(group)} events about '{key}': " + "; ".join(m.text for m in group)
                t = max(m.t for m in group)
                importance = min(1.0, sum(m.importance for m in group) / len(group) + 0.1)
                new_semantics.append(MemoryItem(t, "semantic", summary, importance))
        # 3. Remove episodics that were summarized
        summarized_ids = {id(m) for group in groups.values() if len(group) > 2 for m in group}
        self.items = [m for m in self.items if not (m.kind == "episodic" and id(m) in summarized_ids)]
        # 4. Add new semantic memories
        self.items.extend(new_semantics)
        # 5. Retain all semantic and high-importance, and most recent 200
        keep = [m for m in self.items if m.kind == "semantic" or (m.importance >= 0.7)]
        self.items = (self.items[-200:] + keep)[-300:]
        print(f"DEBUG: Semantic extraction complete. Added {len(new_semantics)} semantic memories. Pruned {len(summarized_ids)} episodics.")
