# sim_ollama.py
from __future__ import annotations
import requests, json, math, random, re, string
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from collections import deque
from datetime import datetime, timedelta
from difflib import SequenceMatcher

# ----------------- Config -----------------
OLLAMA_URL = "http://localhost:11434"

# Use a chat/instruct model (important for /api/chat + format=json)
GEN_MODEL = "llama3.1:8b-instruct-q8_0"   # quantized instruct works well
EMB_MODEL = "nomic-embed-text"

TICK_MINUTES = 5        # 1 tick = 5 minutes
RECENCY_DECAY = 0.85    # per hour

# Map job -> expected workplace (used for routing WORK())
JOB_SITE = {"barista": "Cafe", "junior dev": "Office", "developer": "Office", "engineer": "Office"}

# ----------------- Ollama Client -----------------
class OllamaClient:
    def __init__(self, base_url=OLLAMA_URL, gen_model=GEN_MODEL, emb_model=EMB_MODEL, temperature=0.5):
        self.base = base_url.rstrip("/")
        self.gen_model = gen_model
        self.emb_model = emb_model
        self.temperature = temperature

    # Simple chat (non-JSON critical)
    def generate(self, prompt:str, system:str="", max_tokens:int|None=None) -> str:
        body = {
            "model": self.gen_model,
            "messages": [
                {"role":"system","content":system} if system else {"role":"system","content":BELIEF_LOCK_SYSTEM},
                {"role":"user","content":prompt}
            ],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_ctx": 4096,        # raise to 8192 if you have RAM
                "seed": 1,
                "repeat_penalty": 1.05,
            }
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
            "options": {
                "temperature": self.temperature,
                "num_ctx": 4096,
                "seed": 1,
                "repeat_penalty": 1.05,
            }
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

# ----------------- Inventory Core -----------------
@dataclass(frozen=True)
class Item:
    id: str
    name: str
    tags: set[str]            # {"edible","drink","caffeine"} etc.
    weight: float = 0.0
    effects: Optional[Dict[str, float]] = None  # {"hunger": -0.4, "energy": +0.1}

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
    "money":   Item(id="money",   name="$",        tags={"currency"},                    weight=0.0, effects={}),
    "coffee":  Item(id="coffee",  name="Coffee",   tags={"edible","drink","caffeine"},   weight=0.1, effects={"hunger": -0.2, "energy": +0.15, "stress": -0.02}),
    "pastry":  Item(id="pastry",  name="Pastry",   tags={"edible","food","carb"},        weight=0.2, effects={"hunger": -0.45, "energy": +0.05}),
    "salad":   Item(id="salad",   name="Salad",    tags={"edible","food"},               weight=0.3, effects={"hunger": -0.5, "stress": -0.02}),
    "beans":   Item(id="beans",   name="Coffee Beans", tags={"ingredient"},              weight=0.5, effects={}),
    "sketch":  Item(id="sketch",  name="Sketch",   tags={"art","sellable"},              weight=0.0, effects={}),
}

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
            sim = cosine(qv, (m.vec or []))
            hours_delta = ((latest_t - m.t) * TICK_MINUTES)/60.0  # decay per hour
            rec = RECENCY_DECAY ** hours_delta
            score = 0.6*sim + 0.3*rec + 0.1*m.importance
            scored.append((score, m))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _,m in scored[:k]]

# ----------------- World Model -----------------
@dataclass
class Vendor:
    prices: Dict[str, float]           # item_id -> unit price
    stock: Dict[str, int]              # item_id -> quantity
    buyback: Dict[str, float] = field(default_factory=dict)

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
    capabilities: set[str] = field(default_factory=set)  # e.g., {"food","work_dev","coffee"}
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

ACTION_RE = re.compile(r'^(SAY|MOVE|INTERACT|THINK|PLAN|SLEEP|EAT|WORK|CONTINUE)(\((.*)\))?$')

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

CURRENT_AGENTS_LIST:list[Agent]
@dataclass
class Agent:
    persona:Persona
    place:str
    memory:MemoryStore = field(default_factory=MemoryStore)
    physio:Physio = field(default_factory=Physio)
    plan:List[str]=field(default_factory=list)
    calendar: List[Appointment] = field(default_factory=list)
    inventory: Inventory = field(default_factory=lambda: Inventory(capacity_weight=5.0))

    # runtime state
    last_eat_tick:int = -999
    busy_until:int = -1
    _last_say_tick:int = -999
    _last_plan_tick:int = -999
    _last_diary:str = ""
    _last_diary_tick:int = -999
    _last_interact_tick:int = -999
    _interact_count_window_start:int = -1
    _interact_count:int = 0

    # ---- Helpers ----
    def _normalize_action(self, action: Any) -> str:
        if isinstance(action, dict):
            atype = (action.get("type") or action.get("action") or "THINK").strip()
            payload = {k:v for k,v in action.items() if k not in ("type","action")}
            return f"{atype}({json.dumps(payload)})" if payload else f"{atype}()"
        elif isinstance(action, str):
            s = action.strip()
            if s in ("SAY","MOVE","INTERACT","THINK","PLAN","SLEEP","EAT","WORK","CONTINUE"):
                return f"{s}()"
            m = ACTION_RE.match(s)
            return f"{m.group(1)}{m.group(2) or '()'}" if m else 'THINK({"note":"breathe and reconsider"})'
        else:
            return 'THINK({"note":"invalid action format"})'

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
        return "".join(ch for ch in (s or "").lower().strip() if ch not in string.punctuation)

    def _maybe_write_diary(self, text:str, tick:int):
        if not text: return
        if (tick - self._last_diary_tick) < 6:  # 30 minutes
            return
        norm_new = self._norm_text(text)
        norm_old = self._norm_text(self._last_diary or "")
        sim = SequenceMatcher(None, norm_old, norm_new).ratio()
        if sim < 0.93:
            self.memory.write(MemoryItem(t=tick, kind="autobio", text=text, importance=0.6))
            self._last_diary, self._last_diary_tick = text, tick

    def _coerce_memory_write(self, mw: Any) -> Optional[Tuple[str,str]]:
        def pick_from_dict(d: dict) -> Optional[Tuple[str,str]]:
            for k in ("autobio","episodic","semantic","message","text"):
                v = d.get(k)
                if isinstance(v, str) and v.strip():
                    kind = "autobio" if k=="autobio" else ("semantic" if k=="semantic" else "episodic")
                    return (kind, v.strip())
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

    def _synthesize_plan(self, tick:int) -> List[str]:
        steps: List[str] = []
        workplace = JOB_SITE.get(self.persona.job)
        if workplace and self.place != workplace:
            steps.append(f"MOVE:{workplace}")
        steps.append("WORK:focus")
        minutes = tick * TICK_MINUTES
        if 60 <= minutes <= 180:
            steps.append("EAT:Cafe" if workplace != "Apartment" else "EAT:Apartment")
        return steps

    def _is_valid_place(self, world:World, name:str) -> bool:
        return name in world.places

    def _place_with_capability(self, world:World, cap:str) -> Optional[str]:
        for name, pl in world.places.items():
            if cap in pl.capabilities:
                return name
        return None

    # money helpers (money as item)
    def _pay(self, amount: float) -> bool:
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

    def _interact_allowed(self, tick:int, per_window:int=2, window_ticks:int=6) -> bool:
        if self._interact_count_window_start == -1 or tick - self._interact_count_window_start >= window_ticks:
            self._interact_count_window_start = tick
            self._interact_count = 0
        if self._interact_count >= per_window:
            return False
        self._interact_count += 1
        return True

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
        if self._is_busy(tick):
            return {"action": "CONTINUE()", "private_thought": None, "memory_write": None}

        forced = self.enforce_schedule(tick)
        if forced:
            return {"action": forced[0], "private_thought": f"gotta get to {forced[1]}", "memory_write": None}

        plan_forced = self._maybe_follow_plan()
        if plan_forced:
            return {"action": plan_forced, "private_thought": "stick to plan", "memory_write": None}

        queries = self.recall_queries(obs_text)
        if isinstance(queries, dict):
            queries = list(queries.values())
        mems:List[MemoryItem] = []
        for q in (queries or [])[:6]:
            mems.extend(self.memory.recall(q, k=2))

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
            '  SAY({"to":"ALL","text":"..."})\n'
            '  SAY({"to":"NEARBY","text":"..."})\n'
            '  MOVE({"to":"Cafe"})\n'
            '  INTERACT({"verb":"buy","item":"coffee"})\n'
            '  THINK({"note":"private journaling"})\n'
            '  PLAN({"steps":["MOVE:Office","WORK:focus","EAT:Cafe"]})\n'
            '  SLEEP()\n'
            '  EAT()\n'
            '  WORK()\n\n'
            "Return JSON with exactly these keys:\n"
            "{\n"
            '  "action": string,\n'
            '  "private_thought": string|null,\n'
            '  "memory_write": string | {"autobio"?:string,"episodic"?:string,"semantic"?:string} | null\n'
            "}\n"
            "Rules:\n"
            "- MOVE.to must be the name of an existing place, not an object.\n"
            "- To buy things, use INTERACT({\"verb\":\"buy\",\"item\":\"coffee\"}) at a place with a vendor.\n"
            "- Prefer EAT only if hunger > 0.4 and at most once per 45 minutes.\n"
            "If you choose PLAN, you MUST include {\"steps\": [\"MOVE:Place\", \"WORK:focus\", \"EAT:Cafe\"]}.\n"
            "Return ONLY JSON. No extra text."
            f"- Known people: {', '.join(sorted(a.persona.name for a in CURRENT_AGENTS_LIST ))}\n"
            "- Do NOT mention people who are not in the known-people list.\n"
            "- If unsure who to address, use SAY({\"to\":\"NEARBY\",...}) or SAY({\"to\":\"ALL\",...}).\n"
        )
        txt = ollama.generateJSON(prompt, system=BELIEF_LOCK_SYSTEM, max_tokens=256, force_json=True)
        s = txt.find("{"); e = txt.rfind("}")
        if s!=-1 and e!=-1:
            txt = txt[s:e+1]
        try:
            return json.loads(txt)
        except Exception:
            fix_prompt = f"Fix to valid JSON with keys action, private_thought, memory_write ONLY. Return ONLY JSON.\n```{txt}```"
            txt2 = ollama.generateJSON(fix_prompt, system="You are a strict JSON rewriter.", max_tokens=200, force_json=True)
            s = txt2.find("{"); e = txt2.rfind("}")
            if s!=-1 and e!=-1:
                txt2 = txt2[s:e+1]
            try:
                return json.loads(txt2)
            except Exception:
                return {"action":'SAY({"to":"ALL","text":"Hi there!"})', "private_thought":"be friendly", "memory_write":None}

    def apply_homeostasis(self, action:str):
        a = action.strip()
        # passive drift per tick
        self.physio.energy = max(0.0, self.physio.energy - 0.02)
        self.physio.hunger = min(1.0, self.physio.hunger + 0.02)
        self.physio.stress = min(1.0, self.physio.stress + 0.01)

        if a.startswith("SLEEP"):
            self.physio.energy = min(1.0, self.physio.energy + 0.5)
            self.physio.stress = max(0.0, self.physio.stress - 0.1)
        if a.startswith("EAT"):
            # EAT effects applied in EAT branch via item effects
            pass
        if "INTERACT" in a and "buy" in a:
            pass

        self.physio.mood = "cheerful" if (self.physio.stress < 0.3 and self.physio.energy > 0.5) else "neutral"

    # ---- Act ----
    def act(self, world:World, decision:Dict[str,Any], tick:int):
        action = self._normalize_action(decision.get("action",""))
        priv   = decision.get("private_thought")
        mw_raw = decision.get("memory_write")

        # Silent busy ticks
        if action.startswith("CONTINUE"):
            self.apply_homeostasis(action)
            return

        # route to correct workplace if needed
        if action.startswith("WORK") and not self._work_allowed_here(world):
            target = JOB_SITE.get(self.persona.job, "Office")
            action = f'MOVE({{"to":"{target}"}})'

        # route to food source if needed
        if action.startswith("EAT") and not self._eat_allowed_here(world):
            action = 'MOVE({"to":"Cafe"})'

        # write diary (dedup + rate limit)
        if priv:
            self._maybe_write_diary(priv, tick)

        # coerce memory write
        coerced = self._coerce_memory_write(mw_raw)
        if coerced:
            kind, text = coerced
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
                if not self._is_valid_place(world, dest):
                    action = 'THINK({"note":"can’t go there"})'
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":action, "t":tick})
                else:
                    # travel takes 10 minutes; broadcast once
                    self.busy_until = tick + 2
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"move", "text":action, "t":tick})
                    self.place = dest
            except Exception:
                pass

        elif action.startswith("INTERACT"):
            # cap interact frequency
            if not self._interact_allowed(tick):
                return
            obj, verb, item_id = None, None, None
            try:
                payload = json.loads(action[action.find("(")+1:action.rfind(")")])
                obj = payload.get("object")
                verb = payload.get("verb")
                item_id = payload.get("item") or (obj.lower() if isinstance(obj, str) else None)
                if item_id == "coffeemachine":
                    item_id = "coffee"
            except Exception:
                pass

            place = world.places[self.place]
            vendor = place.vendor

            if verb == "buy" and vendor and item_id in vendor.prices:
                price = vendor.prices[item_id]
                if not vendor.has(item_id, 1):
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":'THINK({"note":"out of stock"})', "t":tick})
                elif not self._pay(price):
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":'THINK({"note":"can’t afford"})', "t":tick})
                elif not self.inventory.add(ITEMS[item_id], 1):
                    self._earn(price)  # refund
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":'THINK({"note":"bags full"})', "t":tick})
                else:
                    vendor.take(item_id, 1)
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"interact", "text":f'BUY({{"item":"{item_id}","$":{price}}})', "t":tick})
                    self.busy_until = tick + 2

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
                world.broadcast(self.place, {"actor":self.persona.name, "kind":"interact", "text":action, "t":tick})
                self.busy_until = tick + 1

        elif action.startswith("EAT"):
            # cooldown 45 min
            if (tick - self.last_eat_tick) < 9:
                # too soon; stay quiet or brief note
                world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":'THINK({"note":"not time to eat"})', "t":tick})
            else:
                edible = self.inventory.find_by_tag("edible")
                if edible:
                    self.inventory.remove(edible.item.id, 1)
                    self._apply_item_effects(edible.item)
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":f'CONSUME({{"item":"{edible.item.id}"}})', "t":tick})
                    self.last_eat_tick = tick
                    self.busy_until = tick + 2
                else:
                    # Try to buy cheapest edible at vendor
                    place = world.places[self.place]; vendor = place.vendor
                    if vendor:
                        edible_options = [(iid, price) for iid, price in vendor.prices.items()
                                          if iid in ITEMS and "edible" in ITEMS[iid].tags and vendor.has(iid,1)]
                        if edible_options:
                            iid, price = sorted(edible_options, key=lambda x: x[1])[0]
                            if self._pay(price) and self.inventory.add(ITEMS[iid], 1):
                                vendor.take(iid, 1)
                                # eat immediately
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
            if self.plan:
                # already have a plan; keep quiet
                pass
            else:
                if (tick - self._last_plan_tick) < 6:
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

        else:
            world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":action, "t":tick})

        # consume plan step if appropriate
        self._consume_plan_if_matches(action)

        # Homeostasis after action
        self.apply_homeostasis(action)

# ------------ LLM World & People Gen (schema + helpers) ------------
ALLOWED_CAPS = {
    "sleep","food_home","food","coffee","work_dev","park","shop","hospital","school","gym","bar","gallery","transit"
}

ITEMS_CATALOG = {
    "coffee": 3.5, "pastry": 4.0, "beans": 12.0, "salad": 3.0
}
ALLOWED_ITEM_IDS = set(ITEMS_CATALOG.keys())

def _coerce_vendor(v):
    if not v: return None
    prices = {k: float(v.get("prices",{}).get(k)) for k in list(v.get("prices",{})) if k in ALLOWED_ITEM_IDS}
    stock  = {k: int(v.get("stock",{}).get(k, 0)) for k in prices.keys()}
    buyback= {k: float(v.get("buyback",{}).get(k)) for k in v.get("buyback",{}) if isinstance(v.get("buyback",{}).get(k),(int,float))}
    for k in list(stock.keys()):
        prices.setdefault(k, ITEMS_CATALOG.get(k, 1.0))
    if not prices: return None
    return Vendor(prices=prices, stock=stock or {k:999 for k in prices}, buyback=buyback)

def _sanitize_caps(caps):
    out = set()
    for c in caps or []:
        c = str(c).strip().lower()
        if c in ALLOWED_CAPS: out.add(c)
    return out

def _ensure_connectivity(places: dict[str, Place]):
    names = list(places.keys())
    if not names: return
    seen=set(); comps=[]
    for n in names:
        if n in seen: continue
        q=[n]; seen.add(n); comp=[n]
        while q:
            cur=q.pop(0)
            for nb in places[cur].neighbors:
                if nb in places and nb not in seen:
                    seen.add(nb); q.append(nb); comp.append(nb)
        comps.append(comp)
    if len(comps)<=1: return
    # connect components pairwise
    for i in range(len(comps)-1):
        a = comps[i][0]; b = comps[i+1][0]
        if b not in places[a].neighbors: places[a].neighbors.append(b)
        if a not in places[b].neighbors: places[b].neighbors.append(a)

def _dedupe_neighbors(places: dict[str, Place]):
    for p in places.values():
        p.neighbors = sorted({nb for nb in p.neighbors if nb in places and nb != p.name})

def llm_generate_places(num_places:int=6, city_name:str="Redwood") -> Dict[str, Place]:
    prompt = f"""
You are designing a small, believable city called {city_name}.
Return ONLY JSON with this shape:

{{
  "places": [
    {{
      "name": "Cafe",
      "neighbors": ["Street","Office"],
      "capabilities": ["food","coffee"],
      "vendor": {{
        "prices": {{"coffee": 3.5, "pastry": 4.0}},
        "stock":  {{"coffee": 999, "pastry": 30}},
        "buyback": {{"sketch": 8.0}}
      }},
      "purpose": "A cozy cafe popular with locals."
    }}
  ]
}}

Rules:
- Create {num_places} places total.
- Names must be unique and human-like (e.g., "Apartment", "Office", "Riverside Park").
- "neighbors" must reference ONLY places that exist in the same JSON.
- Use capabilities realistically (e.g., cafe has "food","coffee"; office has "work_dev").
- Vendors only where it makes sense (cafe/shop/market). No vendor at Street by default.
- Vendor item ids must be a subset of {sorted(list(ALLOWED_ITEM_IDS))} with reasonable prices/stock.
- Return ONLY JSON. No commentary.
"""
    txt = ollama.generateJSON(prompt, system="You return strict JSON only.", max_tokens=1500, force_json=True)
    s=txt.find("{"); e=txt.rfind("}")
    if s!=-1 and e!=-1: txt = txt[s:e+1]
    try:
        data = json.loads(txt)
    except Exception:
        repair = ollama.generateJSON(f"Fix to valid JSON only:\n```{txt}```", system="Return only JSON.", max_tokens=1200, force_json=True)
        s=repair.find("{"); e=repair.rfind("}")
        data = json.loads(repair[s:e+1])

    places: Dict[str, Place] = {}
    for raw in data.get("places", []):
        name = str(raw.get("name","")).strip() or None
        if not name or name in places: continue
        caps = _sanitize_caps(raw.get("capabilities", []))
        vendor = _coerce_vendor(raw.get("vendor"))
        neighbors = [str(x).strip() for x in raw.get("neighbors", []) if isinstance(x,(str,))]
        places[name] = Place(name=name, neighbors=neighbors, capabilities=caps, vendor=vendor)

    _dedupe_neighbors(places)
    _ensure_connectivity(places)
    return places

def llm_generate_personas(num_agents:int=4, city_name:str="Redwood", place_names:List[str]|None=None) -> List[Persona]:
    place_names = place_names or []
    prompt = f"""
Create {num_agents} believable residents of {city_name}.
Return ONLY JSON:

{{
  "people": [
    {{
      "name": "Alice Nguyen",
      "age": 28,
      "job": "barista",
      "bio": "Rents a studio; obsessed with latte art and sketching.",
      "values": ["kindness","stability","creativity"],
      "goals": ["pay rent","improve latte art","make friends"],
      "home": "Apartment"
    }}
  ]
}}

Rules:
- Jobs should map to plausible workplaces (e.g., "junior dev" -> "Office", "barista" -> "Cafe").
- Ages 18–70. Names unique. Return ONLY JSON.
"""
    txt = ollama.generateJSON(prompt, system="You return strict JSON only.", max_tokens=1200, force_json=True)
    s=txt.find("{"); e=txt.rfind("}")
    if s!=-1 and e!=-1: txt = txt[s:e+1]
    try:
        data = json.loads(txt)
    except Exception:
        repair = ollama.generateJSON(f"Fix to valid JSON only:\n```{txt}```", system="Return only JSON.", max_tokens=900, force_json=True)
        s=repair.find("{"); e=repair.rfind("}")
        data = json.loads(repair[s:e+1])

    personas=[]
    names_seen=set()
    for p in data.get("people", []):
        name = str(p.get("name","")).strip()
        if not name or name in names_seen: continue
        names_seen.add(name)
        age  = int(p.get("age", 28))
        job  = str(p.get("job","")).strip().lower() or "unemployed"
        bio  = str(p.get("bio","")).strip() or "Keeps to themself."
        values = [str(v).strip().lower() for v in p.get("values", []) if isinstance(v,str)]
        goals  = [str(v).strip() for v in p.get("goals", []) if isinstance(v,str)]
        personas.append(Persona(name=name, age=age, job=job, city=city_name, bio=bio, values=values[:5], goals=goals[:5]))
    return personas

def build_world_from_llm(num_places=6, city="Redwood") -> World:
    places = llm_generate_places(num_places, city)
    if "Street" not in places:
        places["Street"] = Place("Street", neighbors=[], capabilities=set())
        if places:
            anyp = next(iter(places.keys()))
            places["Street"].neighbors.append(anyp)
            places[anyp].neighbors.append("Street")
    _dedupe_neighbors(places)
    _ensure_connectivity(places)
    return World(places=places)

def spawn_agents_from_llm(world:World, num_agents=4, seed_money=20) -> List[Agent]:
    names = list(world.places.keys())
    personas = llm_generate_personas(num_agents, city_name="Redwood", place_names=names)
    agents=[]
    for persona in personas:
        # choose a start place: Apartment if present else random
        start_place = "Apartment" if "Apartment" in world.places else random.choice(names)
        ag = Agent(persona=persona, place=start_place)
        # calendars based on job
        j = persona.job
        if "dev" in j or "engineer" in j:
            if "Office" in world.places:
                ag.calendar = [Appointment(at_min=60, place="Office", label="standup")]
        elif "barista" in j or "cafe" in j:
            if "Cafe" in world.places:
                ag.calendar = [Appointment(at_min=0, place="Cafe", label="morning shift")]
        # seed money
        ag.inventory.add(ITEMS["money"], seed_money)
        agents.append(ag)
    return agents

# ----------------- Demo -----------------
def _parse_say_payload(text:str) -> Dict[str,Any]:
    """Robustly parse SAY(...) payloads that may use single quotes."""
    raw = text[text.find("(")+1: text.rfind(")")]
    try:
        return json.loads(raw)
    except Exception:
        try:
            return json.loads(raw.replace("'", '"'))
        except Exception:
            return {}

def print_memory_summary(agent: Agent, start: datetime, max_snips: int = 5):
    items = agent.memory.items
    by_kind = {"autobio":0, "episodic":0, "semantic":0, "tom":0}
    for m in items:
        by_kind[m.kind] = by_kind.get(m.kind, 0) + 1

    def fmt_time(tick: int) -> str:
        return now_str(tick, start)

    recent_autobio = sorted((m for m in items if m.kind=="autobio"), key=lambda m: m.t, reverse=True)[:max_snips]
    recent_episodic = sorted((m for m in items if m.kind=="episodic"), key=lambda m: m.t, reverse=True)[:max_snips]
    semantics = [m for m in items if m.kind=="semantic"][:max_snips]

    print(f"\n### {agent.persona.name} – Memory summary")
    print(f"Counts  | autobio={by_kind.get('autobio',0)}  episodic={by_kind.get('episodic',0)}  semantic={by_kind.get('semantic',0)}  tom={by_kind.get('tom',0)}")

    if recent_autobio:
        print("Recent autobio:")
        for m in recent_autobio:
            print(f"  - [{fmt_time(m.t)}] {m.text}")

    if recent_episodic:
        print("Recent episodic:")
        for m in recent_episodic:
            print(f"  - [{fmt_time(m.t)}] {m.text}")

    if semantics:
        print("Semantic facts:")
        for m in semantics:
            print(f"  - {m.text}")


def main():
    random.seed(1)

    start = datetime(2025, 8, 31, 9, 0, 0)

    # === Toggle between static and LLM-generated ===
    USE_LLM_GEN = True

    if USE_LLM_GEN:
        world = build_world_from_llm(num_places=6, city="Redwood")
        agents = spawn_agents_from_llm(world, num_agents=4, seed_money=20)
    else:
        world = World(places={
            "Street":    Place("Street",    ["Apartment","Cafe","Office"], set()),
            "Apartment": Place("Apartment", ["Street"], {"sleep","food_home"}),
            "Cafe":      Place("Cafe",      ["Street"], {"food","coffee"}, vendor=Vendor(
                prices={"coffee":3.5,"pastry":4.0}, stock={"coffee":999,"pastry":40}
            )),
            "Office":    Place("Office",    ["Street"], {"work_dev"}),
        })
        # Example hand-authored agents
        agents = [
            Agent(
                persona=Persona(
                    name="Alice", age=28, job="barista", city="Redwood",
                    bio="I rent a small studio; I love sketching and coffee culture.",
                    values=["kindness","stability","creativity"],
                    goals=["pay rent","improve latte art","make friends"]
                ),
                place="Apartment",
                calendar=[Appointment(at_min=0, place="Cafe", label="morning shift")]
            ),
            Agent(
                persona=Persona(
                    name="Bob", age=31, job="junior dev", city="Redwood",
                    bio="New in town, tight budget, anxious about first week at work.",
                    values=["honesty","learning","security"],
                    goals=["keep new job","save money","meet people"]
                ),
                place="Street",
                calendar=[Appointment(at_min=60, place="Office", label="standup")]
            )
        ]
        for ag in agents:
            ag.inventory.add(ITEMS["money"], 20)

        # Seed some memories (optional)
        agents[0].memory.write(MemoryItem(t=0, kind="semantic", text="Rent is due on the 1st.", importance=0.9))
        agents[0].memory.write(MemoryItem(t=0, kind="semantic", text="Cafe opens at 7:00 and closes at 15:00.", importance=0.7))
        agents[1].memory.write(MemoryItem(t=0, kind="semantic", text="Cafe sells cheap sandwiches.", importance=0.7))
        agents[1].memory.write(MemoryItem(t=0, kind="semantic", text="Office stand-up is usually at 10:00.", importance=0.8))

    global CURRENT_AGENTS_LIST
    CURRENT_AGENTS_LIST = agents
    TICKS = 18*10  # 3 hours at 5-minute ticks
    for t in range(1, TICKS+1):
        print(f'Tick({t}: {now_str(t,start)})')
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

    # Print a small transcript
    print("\n--- Public log (last 30 events) ---")
    for evt in list(world.events)[-30:]:
        ts = now_str(evt['t'], start)
        if evt.get("kind")=="say":
            payload = _parse_say_payload(evt["text"])
            msg = payload.get("text","(…)")
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

    print("\n--- Memory summaries ---")
    for ag in agents:
        print_memory_summary(ag, start, max_snips=4)

    # Inventories
    print("\n--- Inventories ---")
    for ag in agents:
        print(f"{ag.persona.name}: {ag.inventory.to_compact_str()}")

    # Run summary
    print("\n--- Run summary ---")
    for ag in agents:
        print(f"{ag.persona.name} — place={ag.place}, $={ag.inventory.count('money')}, "
              f"energy={ag.physio.energy:.2f}, hunger={ag.physio.hunger:.2f}, stress={ag.physio.stress:.2f}, "
              f"memories={len(ag.memory.items)}")
        
    


if __name__=="__main__":
    main()
