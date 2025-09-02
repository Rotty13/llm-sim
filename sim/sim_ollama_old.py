# sim_ollama.py
from __future__ import annotations
import requests, json, math, random, re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from collections import deque
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import string
from dataclasses import dataclass
from typing import Callable, Optional, Dict, Any, List


# ----------------- Config -----------------
OLLAMA_URL = "http://localhost:11434"

# Use a chat/instruct model (important for /api/chat + format=json)
GEN_MODEL = "llama3.2"   # or "qwen2.5:7b-instruct"
EMB_MODEL = "nomic-embed-text"

TICK_MINUTES = 5        # 1 tick = 5 minutes
RECENCY_DECAY = 0.85    # per hour


# Map job -> expected workplace
JOB_SITE = {"barista": "Cafe", "junior dev": "Office"}

# ----------------- Ollama Client -----------------
class OllamaClient:
    def __init__(self, base_url=OLLAMA_URL, gen_model=GEN_MODEL, emb_model=EMB_MODEL, temperature=0.6):
        self.base = base_url.rstrip("/")
        self.gen_model = gen_model
        self.emb_model = emb_model
        self.temperature = temperature

    # For simple non-JSON generations, if needed
    def generate(self, prompt:str, system:str="", max_tokens:int|None=None) -> str:
        body = {
            "model": self.gen_model,
            "messages": [
                {"role":"system","content":system} if system else {"role":"system","content":BELIEF_LOCK_SYSTEM},
                {"role":"user","content":prompt}
            ],
            "stream": False,
            "options": {"temperature": self.temperature}
        }
        if max_tokens:
            body["options"]["num_predict"] = max_tokens
        r = requests.post(f"{self.base}/api/chat", json=body, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()

    # JSON-strict chat call (uses format=json)
    def generateJSON(self, prompt:str, system:str="", max_tokens:int|None=None, force_json:bool=True) -> str:
        body = {
            "model": self.gen_model,
            "messages": [
                {"role":"system","content":system or BELIEF_LOCK_SYSTEM},
                {"role":"user","content":prompt}
            ],
            "stream": False,
            "options": {"temperature": self.temperature}
        }
        if max_tokens:
            body["options"]["num_predict"] = max_tokens
        if force_json:
            body["format"] = "json"

        r = requests.post(f"{self.base}/api/chat", json=body, timeout=120)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()

    def embed(self, text:str) -> List[float]:
        r = requests.post(f"{self.base}/api/embeddings", json={"model": self.emb_model, "prompt": text}, timeout=120)
        r.raise_for_status()
        return r.json()["embedding"]

ollama = OllamaClient()

# ----------------- Utilities -----------------
def now_str(tick:int, start:datetime) -> str:
    return (start + timedelta(minutes=TICK_MINUTES*tick)).strftime("%Y-%m-%d %H:%M")

def cosine(u:List[float], v:List[float]) -> float:
    if not u or not v or len(u)!=len(v): return 0.0
    su = sum(x*x for x in u); sv = sum(y*y for y in v)
    if su==0 or sv==0: return 0.0
    dot = sum(x*y for x,y in zip(u,v))
    return dot / math.sqrt(su*sv)

# ----------------- Memory -----------------
@dataclass
class MemoryItem:
    t:int
    kind:str          # 'episodic' | 'semantic' | 'autobio' | 'tom'
    text:str
    importance:float=0.5
    vec:Optional[List[float]]=None

class MemoryStore:
    def __init__(self):
        self.items: List[MemoryItem] = []

    def write(self, item:MemoryItem):
        # lazily embed when first inserted
        if item.vec is None:
            try:
                item.vec = ollama.embed(item.text)
            except Exception:
                item.vec = []
        self.items.append(item)

    def recall(self, q:str, k:int=5) -> List[MemoryItem]:
        if not self.items: return []
        try:
            qv = ollama.embed(q)
        except Exception:
            qv = []

        latest_t = max(m.t for m in self.items) if self.items else 0
        scored=[]
        for m in self.items:
            sim = cosine(qv, m.vec or [])
            # decay per hour (tick->minutes -> /60)
            hours_delta = ((latest_t - m.t) * TICK_MINUTES)/60.0
            rec = RECENCY_DECAY ** hours_delta
            score = 0.6*sim + 0.3*rec + 0.1*m.importance
            scored.append((score, m))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _,m in scored[:k]]

# ----------------- World Model -----------------
@dataclass
class Vendor:
    prices: Dict[str, float]           # item_id -> unit price
    stock: Dict[str, int]              # item_id -> quantity (use big numbers for “infinite”)
    buyback: Dict[str, float] = field(default_factory=dict)  # item_id -> price vendor pays

    def has(self, item_id: str, qty: int=1) -> bool:
        return self.stock.get(item_id, 0) >= qty

    def take(self, item_id: str, qty: int=1) -> bool:
        if not self.has(item_id, qty): return False
        self.stock[item_id] -= qty
        return True

    def restock(self, item_id: str, qty: int):
        self.stock[item_id] = self.stock.get(item_id, 0) + qty

@dataclass
class Place:
    name:str
    neighbors:List[str]
    capabilities: set[str] = field(default_factory=set)
    vendor: Optional[Vendor] = None

@dataclass
class World:
    places: Dict[str, Place]
    events: deque = field(default_factory=deque)

    def broadcast(self, place:str, payload:Dict[str,Any]):
        self.events.append({"place":place, **payload})

# ----------------- Agent -----------------
BELIEF_LOCK_SYSTEM = (
    "You are a human being living in a small city simulation. "
    "You are not an AI model. You experience time, fatigue, hunger, and emotions. "
    "Stay in-world; never mention simulations or models unless explicitly asked in-world."
)

ACTION_RE = re.compile(r'^(SAY|MOVE|INTERACT|THINK|PLAN|SLEEP|EAT|WORK)(\((.*)\))?$')

@dataclass
class Persona:
    name:str
    age:int
    job:str
    city:str
    bio:str
    values:List[str]
    goals:List[str]

@dataclass
class Physio:
    energy:float=1.0
    hunger:float=0.2
    stress:float=0.2
    mood:str="neutral"

@dataclass
class Appointment:
    at_min:int
    place:str
    label:str  # e.g., "standup"

@dataclass(frozen=True)
class Item:
    id: str
    name: str
    tags: set[str]            # e.g., {"edible","drink","caffeine"}
    weight: float = 0.0
    effects: Dict[str, float] = None  # e.g., {"hunger": -0.4, "energy": +0.1}

@dataclass
class ItemStack:
    item: Item
    qty: int = 1

class Inventory:
    def __init__(self, capacity_weight: float = 9999.0):
        self.stacks: List[ItemStack] = []
        self.capacity_weight = capacity_weight

    def _current_weight(self) -> float:
        return sum(s.item.weight * s.qty for s in self.stacks)

    def can_add(self, item: Item, qty: int = 1) -> bool:
        return self._current_weight() + item.weight * qty <= self.capacity_weight

    def add(self, item: Item, qty: int = 1) -> bool:
        if not self.can_add(item, qty): return False
        for s in self.stacks:
            if s.item.id == item.id:
                s.qty += qty
                return True
        self.stacks.append(ItemStack(item, qty))
        return True

    def has(self, item_id: str, qty: int = 1) -> bool:
        total = 0
        for s in self.stacks:
            if s.item.id == item_id:
                total += s.qty
                if total >= qty: return True
        return False

    def remove(self, item_id: str, qty: int = 1) -> bool:
        needed = qty
        for s in list(self.stacks):
            if s.item.id == item_id:
                take = min(s.qty, needed)
                s.qty -= take
                needed -= take
                if s.qty <= 0: self.stacks.remove(s)
                if needed <= 0: return True
        return False

    def find_by_tag(self, tag: str) -> Optional[ItemStack]:
        for s in self.stacks:
            if tag in s.item.tags and s.qty > 0:
                return s
        return None

    def count(self, item_id: str) -> int:
        return sum(s.qty for s in self.stacks if s.item.id == item_id)

    def to_compact_str(self) -> str:
        return ", ".join(f"{s.item.name} x{s.qty}" for s in self.stacks) or "(empty)"


# ----------------- Items Catalog -----------------
ITEMS: Dict[str, Item] = {
    "money":   Item(id="money",   name="$",        tags={"currency"},     weight=0.0, effects={}),
    "coffee":  Item(id="coffee",  name="Coffee",   tags={"edible","drink","caffeine"}, weight=0.1, effects={"hunger": -0.2, "energy": +0.15, "stress": -0.02}),
    "pastry":  Item(id="pastry",  name="Pastry",   tags={"edible","food","carb"},      weight=0.2, effects={"hunger": -0.45, "energy": +0.05}),
    "salad":   Item(id="salad",   name="Salad",    tags={"edible","food"},             weight=0.3, effects={"hunger": -0.5, "stress": -0.02}),
    "beans":   Item(id="beans",   name="Coffee Beans", tags={"ingredient"},            weight=0.5, effects={}),
    "sketch":  Item(id="sketch",  name="Sketch",   tags={"art","sellable"},            weight=0.0, effects={}),
}

world:World

@dataclass
class Agent:
    persona:Persona
    place:str
    memory:MemoryStore = field(default_factory=MemoryStore)
    physio:Physio = field(default_factory=Physio)
    plan:List[str]=field(default_factory=list)
    calendar: List[Appointment] = field(default_factory=lambda: [Appointment(at_min=60, place="Office", label="standup")])
    inventory: Inventory = field(default_factory=lambda: Inventory(capacity_weight=5.0))

    # runtime state
    last_eat_tick:int = -999
    busy_until:int = -1
    _last_say_tick:int = -999
    _last_diary:str = ""
    _last_diary_tick:int = -999
    _last_plan_tick:int = -999

    # ---- Helpers ----



    def _normalize_action(self, action: Any) -> str:
        """
        Convert model output (string or dict) into a canonical DSL string.
        Examples:
        {"type":"PLAN","steps":["EAT:Cafe","WORK:focus"]}
            -> 'PLAN({"steps":["EAT:Cafe","WORK:focus"]})'
        {"type":"MOVE","to":"Cafe"}
            -> 'MOVE({"to":"Cafe"})'
        "WORK" -> "WORK()"
        """
        if isinstance(action, dict):
            atype = action.get("type") or action.get("action") or "THINK"
            payload = {k:v for k,v in action.items() if k not in ("type","action")}
            if payload:
                return f"{atype}({json.dumps(payload)})"
            else:
                return f"{atype}()"
        elif isinstance(action, str):
            m = ACTION_RE.match(action.strip())
            if not m:
                return 'THINK({"note":"breathe and reconsider"})'
            verb = m.group(1)
            args = m.group(2) or "()"
            return f"{verb}{args}"
        else:
            return 'THINK({"note":"invalid action format"})'

    def _validate_action(self, action:str) -> str:
        m = ACTION_RE.match(action.strip())
        if not m:
            return 'THINK({"note":"breathe and reconsider"})'
        verb = m.group(1)
        args = m.group(2) or "()"
        return f"{verb}{args}"

    def _place_has(self, world:World, cap:str) -> bool:
        return cap in world.places[self.place].capabilities

    def _work_allowed_here(self, world:World) -> bool:
        expected = JOB_SITE.get(self.persona.job)
        return bool(expected) and self.place == expected

    def _eat_allowed_here(self, world:World) -> bool:
        return self._place_has(world, "food") or self._place_has(world, "food_home")

    def _is_busy(self, tick:int) -> bool:
        return tick < self.busy_until

    def _norm_text(self, s:str) -> str:
        return "".join(ch for ch in s.lower().strip() if ch not in string.punctuation)


    def _maybe_write_diary(self, text:str, tick:int):
        if not text: return
        if (tick - self._last_diary_tick) < 6:  # 30 min
            return
        norm_new = self._norm_text(text)
        norm_old = self._norm_text(self._last_diary or "")
        from difflib import SequenceMatcher
        if SequenceMatcher(None, norm_old, norm_new).ratio() < 0.93:
            self.memory.write(MemoryItem(t=tick, kind="autobio", text=text, importance=0.6))
            self._last_diary, self._last_diary_tick = text, tick

    # ---- Plan execution (simple) ----
    def _maybe_follow_plan(self) -> Optional[str]:
        if not self.plan:
            return None
        head = self.plan[0]
        if head.startswith("MOVE:"):
            dest = head.split(":",1)[1]
            return f'MOVE({{"to":"{dest}"}})'
        if head.startswith("WORK:"):
            return 'WORK()'
        if head.startswith("EAT:"):
            return 'EAT()'
        return None

    def _consume_plan_if_matches(self, action:str):
        if not self.plan: return
        head = self.plan[0]
        if head.startswith("MOVE:") and action.startswith("MOVE"):
            try:
                payload = json.loads(action[action.find("(")+1:action.rfind(")")])
                if head.split(":",1)[1] == payload.get("to",""):
                    self.plan.pop(0)
            except Exception:
                pass
        elif head.startswith("WORK:") and action.startswith("WORK"):
            self.plan.pop(0)
        elif head.startswith("EAT:") and action.startswith("EAT"):
            self.plan.pop(0)

    def _synthesize_plan(self, tick:int) -> list[str]:
        """If the model returns PLAN without steps, make a tiny reasonable plan."""
        steps: list[str] = []
        workplace = JOB_SITE.get(self.persona.job)
        # Go to workplace if not already there
        if workplace and self.place != workplace:
            steps.append(f"MOVE:{workplace}")
        # Do some work
        steps.append("WORK:focus")
        # If mid-morning, plan to eat at nearest reasonable spot
        minutes = tick * TICK_MINUTES
        if 60 <= minutes <= 180:
            steps.append("EAT:Cafe" if workplace != "Apartment" else "EAT:Apartment")
        return steps
    
    def _coerce_memory_write(self, mw: Any) -> Optional[tuple[str,str]]:
        """
        Returns (kind, text) or None.
        Accepts strings, dicts with semantic/episodic/autobio/message/text, or lists of such.
        Ignores timestamps; we stamp with current tick.
        """
        def pick_from_dict(d: dict) -> Optional[tuple[str,str]]:
            # direct known keys
            for k in ("autobio","episodic","semantic","message","text"):
                v = d.get(k)
                if isinstance(v, str) and v.strip():
                    kind = "autobio" if k == "autobio" else ("semantic" if k=="semantic" else "episodic")
                    return (kind, v.strip())
            # timestamp-shaped or nested dicts
            for v in d.values():
                if isinstance(v, str) and v.strip():
                    return ("episodic", v.strip())
                if isinstance(v, dict):
                    got = pick_from_dict(v)
                    if got: return got
            return None

        if mw is None:
            return None
        if isinstance(mw, str):
            s = mw.strip()
            return ("episodic", s) if s else None
        if isinstance(mw, dict):
            return pick_from_dict(mw)
        if isinstance(mw, list):
            for item in mw:
                got = self._coerce_memory_write(item)
                if got: return got
        return None

    # ---- Schedule enforcement ----
    def enforce_schedule(self, tick:int) -> Optional[tuple[str,str]]:
        minutes = (tick * TICK_MINUTES)
        for appt in self.calendar:
            if 0 <= appt.at_min - minutes <= 15:   # within 15 min window
                if self.place != appt.place:
                    return (f'MOVE({{"to":"{appt.place}"}})', appt.place)
        return None

    # ---- Recall prompt (asks for search queries) ----
    def recall_queries(self, observation:str) -> List[str]:
        prompt = (
            f"You are {self.persona.name}, a human {self.persona.job} in {self.persona.city}.\n"
            f"Recent perception: {observation}\n"
            f"Top goals: {', '.join(self.persona.goals[:3])}\n\n"
            "Return up to 6 short memory search queries (JSON list only, no prose)."
        )
        try:
            txt = ollama.generateJSON(prompt, system=BELIEF_LOCK_SYSTEM, max_tokens=256, force_json=True)
            return json.loads(txt)
        except Exception:
            return ["today", "schedule", "lunch", "rent", "friend", "work"]

    # ---- Decide (choose 1 Action DSL step) ----
    def decide(self, obs_text:str, tick:int, start:datetime) -> Dict[str,Any]:
        # If busy, keep it simple this tick
        if self._is_busy(tick):
            return {"action": "CONTINUE()", "private_thought": None, "memory_write": None}

        # Hard schedule enforcement (e.g., stand-up)
        forced = self.enforce_schedule(tick)
        if forced:
            return {"action": forced[0], "private_thought": f"gotta get to {forced[1]}", "memory_write": None}

        # Simple plan executor
        plan_forced = self._maybe_follow_plan()
        if plan_forced:
            return {"action": plan_forced, "private_thought": "stick to plan", "memory_write": None}

        # Otherwise use LLM
        queries = self.recall_queries(obs_text)
        mems:List[MemoryItem] = []
        if type(queries) == dict:
            queries = list(queries.values())
        for q in queries[:6]:
            mems.extend(self.memory.recall(q, k=2))

        # dedupe + format
        seen=set(); rel=[]
        for m in mems:
            if id(m) in seen: continue
            seen.add(id(m))
            rel.append(f"[{now_str(m.t,start)}] {m.kind}: {m.text}")

        prompt = (
            f"You are {self.persona.name} (bio: {self.persona.bio}). "
            f"Time {now_str(tick,start)}. Location {self.place}. Mood {self.physio.mood}. "
            f"Needs: energy={self.physio.energy:.2f}, hunger={self.physio.hunger:.2f}, stress={self.physio.stress:.2f}.\n"
            "Relevant memories:\n" + ("\n".join(rel) if rel else "(none)") + "\n"
            f"Day plan (remaining steps): {self.plan}\n\n"
            "Choose ONE human-realistic action from this DSL and a private thought ≤20 words.\n"
            "ACTION DSL (JSON lines examples):\n"
            '  SAY({"to":"Alice","text":"..."})\n'
            '  MOVE({"to":"Cafe"})\n'
            '  INTERACT({"object":"CoffeeMachine","verb":"buy"})\n'
            '  THINK({"note":"private journaling"})\n'
            '  PLAN({"steps":["MOVE:Office","WORK:focus","EAT:Cafe"]})\n'
            '  SLEEP()\n'
            '  EAT()\n'
            '  WORK()\n\n'
            "Output strict JSON with keys: action, private_thought, memory_write (nullable)."
            '''Return JSON with exactly these keys:
                {
                "action": string,  // one of 'SAY({...})','MOVE({...})','INTERACT({...})','THINK({...})','PLAN({"steps":[...]})','SLEEP()','EAT()','WORK()'
                "private_thought": string|null,
                "memory_write": string | {"autobio"?:string,"episodic"?:string,"semantic"?:string} | null
                }
                If you choose PLAN, you MUST include {"steps":[ "MOVE:Place", "WORK:focus", "EAT:Cafe" ]}.
                No extra keys. No prose outside JSON.
                - Prefer EAT only if hunger > 0.4 and at most once per 45 minutes.
                - To buy things, use INTERACT({"verb":"buy","item":"coffee"}) at places with vendors.'''
            'Rules:'
            f'- MOVE.to MUST be one of: {list(world.places.keys())} only.'
            '- INTERACT uses {"object":"Coffee","verb":"buy"} and happens at a place; never MOVE to an object.'
        )
        txt = ollama.generateJSON(prompt, system=BELIEF_LOCK_SYSTEM, max_tokens=256, force_json=True)
        # be robust to stray text
        start_brace = txt.find("{")
        end_brace   = txt.rfind("}")
        if start_brace!=-1 and end_brace!=-1:
            txt = txt[start_brace:end_brace+1]
        try:
            return json.loads(txt)
        except Exception:
            # minimal safe fallback policy
            return {"action":'SAY({"to":"ALL","text":"Hi there!"})', "private_thought":"be friendly", "memory_write":None}

    def apply_homeostasis(self, action:str):
        a = action.strip()
        # passive drift per tick
        self.physio.energy = max(0.0, self.physio.energy - 0.02)  # slower decay
        self.physio.hunger = min(1.0, self.physio.hunger + 0.02)
        self.physio.stress = min(1.0, self.physio.stress + 0.01)

        if a.startswith("SLEEP"):
            self.physio.energy = min(1.0, self.physio.energy + 0.5)
            self.physio.stress = max(0.0, self.physio.stress - 0.1)
        if a.startswith("EAT"):
            self.physio.hunger = max(0.0, self.physio.hunger - 0.6)
        if "INTERACT" in a and "buy" in a:
            self.physio.hunger = max(0.0, self.physio.hunger - 0.4)

        self.physio.mood = "cheerful" if (self.physio.stress < 0.3 and self.physio.energy > 0.5) else "neutral"

    def _pay(self, amount: float) -> bool:
        # uses whole dollars; extend if you want cents
        needed = int(round(amount))
        if self.inventory.count("money") < needed:
            return False
        self.inventory.remove("money", needed)
        return True

    def _earn(self, amount: float):
        self.inventory.add(ITEMS["money"], int(round(amount)))

    def _apply_item_effects(self, item: Item):
        eff = item.effects or {}
        if "hunger" in eff:
            self.physio.hunger = max(0.0, self.physio.hunger + eff["hunger"])
        if "energy" in eff:
            self.physio.energy = min(1.0, self.physio.energy + eff["energy"])
        if "stress" in eff:
            self.physio.stress = max(0.0, self.physio.stress + eff["stress"])

    # ---- Act ----
    def act(self, world:World, decision:Dict[str,Any], tick:int):
        action = self._normalize_action(decision.get("action",""))
        priv   = decision.get("private_thought")
        memw   = decision.get("memory_write")

        if action.startswith("CONTINUE"):
            # Stay quiet while busy; do not broadcast.
            self.apply_homeostasis(action)
            return

        # route to correct workplace if needed
        if action.startswith("WORK") and not self._work_allowed_here(world):
            target = JOB_SITE.get(self.persona.job, "Office")
            action = f'MOVE({{"to":"{target}"}})'

        # route to food source if needed
        if action.startswith("EAT") and not self._eat_allowed_here(world):
            action = 'MOVE({"to":"Cafe"})'

        # write diaries / episodic
        if priv:
            self._maybe_write_diary(priv, tick)

        mw = self._coerce_memory_write(decision.get("memory_write"))
        if mw:
            kind, text = mw
            self.memory.write(MemoryItem(t=tick, kind=kind, text=text, importance=0.6))

        # SAY (rate-limited 30 minutes)
        if action.startswith("SAY"):
            if (tick - self._last_say_tick) >= 6:
                world.broadcast(self.place, {"actor":self.persona.name, "kind":"say", "text":action, "t":tick})
                self._last_say_tick = tick

        elif action.startswith("MOVE"):
            try:
                payload = json.loads(action[action.find("(")+1:action.rfind(")")])
                dest = payload["to"]
                # start moving
                self.busy_until = tick + 2   # 10 minutes travel
                # (optional) broadcast a single movement start
                world.broadcast(self.place, {"actor":self.persona.name, "kind":"move", "text":action, "t":tick})
                # arrive at destination at the end of the move block
                self.place = dest
            except Exception:
                pass

        elif action.startswith("EAT"):
            # cooldown 45 min
            if (tick - self.last_eat_tick) < 9:
                # silently drop to THINK
                action = 'THINK({"note":"not time to eat"})'
                world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":action, "t":tick})
            else:
                # Try to consume an edible item from inventory
                edible = self.inventory.find_by_tag("edible")
                if edible:
                    self.inventory.remove(edible.item.id, 1)
                    self._apply_item_effects(edible.item)
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":f'CONSUME({{"item":"{edible.item.id}"}})', "t":tick})
                    self.last_eat_tick = tick
                    self.busy_until = tick + 2
                else:
                    # If at vendor place with edible items, try to auto-buy cheapest edible then eat
                    place = world.places[self.place]
                    vendor = place.vendor
                    if vendor:
                        # find cheapest edible available
                        edible_options = [(iid, price) for iid, price in vendor.prices.items() if "edible" in (ITEMS.get(iid).tags if ITEMS.get(iid) else set()) and vendor.has(iid,1)]
                        if edible_options:
                            iid, price = sorted(edible_options, key=lambda x: x[1])[0]
                            if self._pay(price) and self.inventory.add(ITEMS[iid], 1):
                                vendor.take(iid, 1)
                                # immediately consume
                                self.inventory.remove(iid, 1)
                                self._apply_item_effects(ITEMS[iid])
                                world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":f'BUY+EAT({{"item":"{iid}","$":{price}}})', "t":tick})
                                self.last_eat_tick = tick
                                self.busy_until = tick + 2
                            else:
                                world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":'THINK({"note":"can’t buy food"})', "t":tick})
                        else:
                            world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":'THINK({"note":"no food here"})', "t":tick})
                    else:
                        world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":'THINK({"note":"no food available"})', "t":tick})

        elif action.startswith("WORK"):
            world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":"WORK()", "t":tick})
            self.busy_until = tick + 3  # 15 minutes

        elif action.startswith("PLAN"):
            # If we already have steps, don't re-plan
            if self.plan:
                # show a small think once (optional) or stay silent:
                # world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":'THINK({"note":"using current plan"})', "t":tick})
                pass
            else:
                if (tick - self._last_plan_tick) < 6:
                    # keep silent (no spam)
                    pass
                else:
                    self._last_plan_tick = tick
                    steps = []
                    try:
                        payload = json.loads(action[action.find("(")+1:action.rfind(")")]) or {}
                        steps = payload.get("steps") if isinstance(payload.get("steps"), list) else []
                    except Exception:
                        steps = []
                    if not steps:
                        steps = self._synthesize_plan(tick)
                    if steps:
                        self.plan = steps
                        world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":"PLAN", "t":tick})
        elif action.startswith("INTERACT"):
            # parsed payload (object/item/verb)
            obj, verb, item_id = None, None, None
            try:
                payload = json.loads(action[action.find("(")+1:action.rfind(")")])
                obj = payload.get("object")
                verb = payload.get("verb")
                item_id = payload.get("item") or (obj.lower() if isinstance(obj, str) else None)
                # map friendly names to ids
                if item_id in ("coffee","pastry","beans","salad","sketch","money"):
                    pass
                elif item_id == "coffeemachine":
                    item_id = "coffee"
            except Exception:
                pass

            place = world.places[self.place]
            vendor = place.vendor

            # BUY
            if verb == "buy" and vendor and item_id in vendor.prices:
                price = vendor.prices[item_id]
                if not vendor.has(item_id, 1):
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":'THINK({"note":"out of stock"})', "t":tick})
                elif not self._pay(price):
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":'THINK({"note":"can’t afford"})', "t":tick})
                elif not self.inventory.add(ITEMS[item_id], 1):
                    # refund if overweight
                    self._earn(price)
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":'THINK({"note":"bags full"})', "t":tick})
                else:
                    vendor.take(item_id, 1)
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"interact", "text":f'BUY({{"item":"{item_id}","$":{price}}})', "t":tick})
                    self.busy_until = tick + 2

            # SELL
            elif verb == "sell" and vendor and item_id in (vendor.buyback or {}):
                if not self.inventory.has(item_id, 1):
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":'THINK({"note":"nothing to sell"})', "t":tick})
                else:
                    self.inventory.remove(item_id, 1)
                    self._earn(vendor.buyback[item_id])
                    vendor.restock(item_id, 1)
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"interact", "text":f'SELL({{"item":"{item_id}","$":{vendor.buyback[item_id]}}})', "t":tick})
                    self.busy_until = tick + 2

            else:
                # generic interact (non-vending) stays as is
                world.broadcast(self.place, {"actor":self.persona.name, "kind":"interact", "text":action, "t":tick})
                self.busy_until = tick + 1
        else:
            # SLEEP/THINK
            world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":action, "t":tick})

        # consume plan step if appropriate
        self._consume_plan_if_matches(action)

        # Homeostasis after action
        self.apply_homeostasis(action)

# ----------------- Demo -----------------
def main():
    random.seed(1)

    start = datetime(2025, 8, 31, 9, 0, 0)
    global world
    world = World(places={
        "Street":    Place("Street",    ["Apartment","Cafe","Office"], set()),
        "Apartment": Place("Apartment", ["Street"], {"sleep","food_home"}, vendor=Vendor(
            prices={"salad": 3.0}, stock={"salad": 5}  # simple home-food example
        )),
        "Cafe":      Place("Cafe",      ["Street"], {"food","coffee"}, vendor=Vendor(
            prices={"coffee": 3.5, "pastry": 4.0, "beans": 12.0},
            stock={"coffee": 999, "pastry": 40, "beans": 10},
            buyback={"sketch": 8.0}
        )),
        "Office":    Place("Office",    ["Street"], {"work_dev"}),
    })

    alice = Agent(
        persona=Persona(
            name="Alice", age=28, job="barista", city="Redwood",
            bio="I rent a small studio; I love sketching and coffee culture.",
            values=["kindness","stability","creativity"],
            goals=["pay rent","improve latte art","make friends"]
        ),
        place="Apartment",
        calendar=[Appointment(at_min=0, place="Cafe", label="morning shift")]
    )
    bob = Agent(
        persona=Persona(
            name="Bob", age=31, job="junior dev", city="Redwood",
            bio="New in town, tight budget, anxious about first week at work.",
            values=["honesty","learning","security"],
            goals=["keep new job","save money","meet people"]
        ),
        place="Street",
        calendar=[Appointment(at_min=60, place="Office", label="standup")] 
    )
    agents=[alice,bob]
    alice.inventory.add(ITEMS["money"], 25)   # $25
    bob.inventory.add(ITEMS["money"], 15)     # $15

    # Seed memories (embedded lazily)
    alice.memory.write(MemoryItem(t=0, kind="semantic", text="Rent is due on the 1st.", importance=0.9))
    alice.memory.write(MemoryItem(t=0, kind="semantic", text="Cafe opens at 7:00 and closes at 15:00.", importance=0.7))
    bob.memory.write(MemoryItem(t=0, kind="semantic", text="Cafe sells cheap sandwiches.", importance=0.7))
    bob.memory.write(MemoryItem(t=0, kind="semantic", text="Office stand-up is usually at 10:00.", importance=0.8))

    TICKS = 36  # 3 hours at 5-minute ticks
    for t in range(1, TICKS+1):
        # Perceive current public events in same place
        perceptions:Dict[str,str] = {}
        for ag in agents:
            obs = []
            for evt in list(world.events):
                if evt.get("place")==ag.place and evt.get("actor")!=ag.persona.name:
                    kind = evt.get("kind"); text = evt.get("text","")
                    obs.append(f"{evt['actor']} {kind} {text}")
            perceptions[ag.persona.name] = "; ".join(obs) if obs else "(quiet)"

        # Decide and act
        for ag in agents:
            decision = ag.decide(perceptions[ag.persona.name], t, start)
            ag.act(world, decision, t)

        # trim event queue
        if len(world.events) > 256:
            for _ in range(64): world.events.popleft()

    def _parse_payload(text:str):
        raw = text[text.find("(")+1: text.rfind(")")]
        try:
            return json.loads(raw)
        except Exception:
            # naive fix: convert single to double quotes (handles simple cases)
            try:
                return json.loads(raw.replace("'", '"'))
            except Exception:
                return {}

    # Print a small transcript
    print("\n--- Public log (last 30 events) ---")
    for evt in list(world.events)[-30:]:
        ts = now_str(evt['t'], start)
        if evt.get("kind")=="say":
            # extract JSON payload
            try:
                payload = _parse_payload(evt["text"])
                msg = payload.get("text","(…)")
            except:
                msg = evt["text"]
            print(f"[{ts} @ {evt['place']}] {evt['actor']}: {msg}")
        elif evt.get("kind")=="act":
            print(f"[{ts} @ {evt['place']}] {evt['actor']} {evt['text']}")
        elif evt.get("kind")=="move":
            try:
                payload = json.loads(evt["text"][evt["text"].find("(")+1: evt["text"].rfind(")")])
                dest = payload.get("to","?")
                print(f"[{ts} @ {evt['place']}] {evt['actor']} MOVE → {dest}")
            except:
                print(f"[{ts} @ {evt['place']}] {evt['actor']} MOVE")

    print("\n--- Alice diary snippets ---")
    for m in alice.memory.items:
        if m.kind=="autobio": print("-", m.text)

    print("\n--- Bob diary snippets ---")
    for m in bob.memory.items:
        if m.kind=="autobio": print("-", m.text)

    def summary(agent:Agent, name:str):
        print(f"{name} — place={agent.place}, wallet=${0:.2f}, "
            f"energy={agent.physio.energy:.2f}, hunger={agent.physio.hunger:.2f}, stress={agent.physio.stress:.2f}, "
            f"memories={len(agent.memory.items)}")

    print("\n--- Run summary ---")
    summary(alice, "Alice")
    summary(bob, "Bob")

    print("\n--- Inventories ---")
    print(f"Alice: {alice.inventory.to_compact_str()}")
    print(f"Bob:   {bob.inventory.to_compact_str()}")

if __name__=="__main__":
    main()
