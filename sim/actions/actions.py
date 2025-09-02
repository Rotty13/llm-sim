from __future__ import annotations
import json, re
from typing import Any

ACTION_RE = re.compile(r'^(SAY|MOVE|INTERACT|THINK|PLAN|SLEEP|EAT|WORK|CONTINUE)(\((.*)\))?$')

def normalize_action(action: Any) -> str:
    """Accept dict or string, return canonical DSL string."""
    if isinstance(action, dict):
        atype = (action.get("type") or action.get("action") or "THINK").strip()
        payload = {k:v for k,v in action.items() if k not in ("type","action")}
        return f"{atype}({json.dumps(payload)})" if payload else f"{atype}()"
    if isinstance(action, str):
        s = action.strip()
        if s in ("SAY","MOVE","INTERACT","THINK","PLAN","SLEEP","EAT","WORK","CONTINUE"):
            return f"{s}()"
        m = ACTION_RE.match(s)
        return f"{m.group(1)}{m.group(2) or '()'}" if m else 'THINK({"note":"breathe and reconsider"})'
    return 'THINK({"note":"invalid action format"})'
