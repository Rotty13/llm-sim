"""
utils.py

Provides shared utility functions for time formatting and vector similarity in llm-sim.
Used throughout simulation modules for time calculations and mathematical operations.

Key Functions:
- now_str: Format simulation time from tick and start datetime.
- cosine: Calculate cosine similarity between two vectors.

LLM Usage:
- None directly; utility functions may be used by modules that interact with LLMs.

CLI Arguments:
- None directly; utilities are used by simulation modules and scripts.
"""
# Utility functions
import math
from datetime import datetime, timedelta
from typing import List

TICK_MINUTES = 5

def now_str(tick: int, start: datetime) -> str:
    return (start + timedelta(minutes=TICK_MINUTES * tick)).strftime("%Y-%m-%d %H:%M")

def cosine(u: List[float], v: List[float]) -> float:
    if not u or not v or len(u) != len(v): return 0.0
    su = sum(x * x for x in u)
    sv = sum(y * y for y in v)
    if su == 0 or sv == 0: return 0.0
    dot = sum(x * y for x, y in zip(u, v))
    return dot / math.sqrt(su * sv)
