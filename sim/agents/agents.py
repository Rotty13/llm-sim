from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
import json, string

from matplotlib.pylab import f

from ..llm.llm import llm, BELIEF_LOCK_SYSTEM
from ..memory.memory import MemoryStore, MemoryItem
from ..actions.actions import normalize_action
from ..world.world import World
from ..scheduler.scheduler import Appointment, enforce_schedule
from ..inventory.inventory import Inventory

def now_str(tick:int, start_dt) -> str:
    from datetime import timedelta
    return (start_dt + timedelta(minutes=5*tick)).strftime("%Y-%m-%d %H:%M")

@dataclass
class Persona:
    name: str
    age: int
    job: str
    city: str
    bio: str
    values: List[str]
    goals: List[str]

@dataclass
class Physio:
    energy: float = 1.0
    hunger: float = 0.2
    stress: float = 0.2
    mood: str = "neutral"

JOB_SITE = {"barista":"Cafe", "junior dev":"Office", "developer":"Office", "engineer":"Office"}

@dataclass
class Agent:
    persona: Persona
    place: str
    memory: MemoryStore = field(default_factory=MemoryStore)
    physio: Physio = field(default_factory=Physio)
    plan: List[str] = field(default_factory=list)
    calendar: List[Appointment] = field(default_factory=list)
    inventory: Inventory = field(default_factory=lambda: Inventory(capacity_weight=5.0))
    obs_list: List[str] = field(default_factory=list)

    # runtime
    busy_until: int = -1
    _last_say_tick: int = -999
    _last_diary_tick: int = -999
    _last_diary: str = ""

    def add_observation(self, text:str):
        if text and text not in self.obs_list:
            self.obs_list.append(text)
            if len(self.obs_list) > 20:
                self.obs_list.pop(0)

    def _norm_text(self, s:str) -> str:
        return "".join(ch for ch in (s or "").lower().strip() if ch not in string.punctuation)

    def _maybe_write_diary(self, text:str, tick:int):
        if not text: return
        if (tick - self._last_diary_tick) < 6: return
        sim = SequenceMatcher(None, self._norm_text(self._last_diary), self._norm_text(text)).ratio()
        if sim < 0.93:
            self.memory.write(MemoryItem(t=tick, kind="autobio", text=text, importance=0.6))
            self._last_diary, self._last_diary_tick = text, tick

    def _work_allowed_here(self, world:World) -> bool:
        expected = JOB_SITE.get(self.persona.job)
        return bool(expected) and self.place == expected

    def _eat_allowed_here(self, world:World) -> bool:
        p = world.places[self.place]
        return "food" in p.capabilities or "food_home" in p.capabilities

    def decide(self, world: World, obs_text:str, tick:int, start_dt) -> Dict[str,Any]:
        if tick < self.busy_until:
            return {"action": "CONTINUE()", "private_thought": None, "memory_write": None}

        #forced = enforce_schedule(self.calendar, self.place, tick)
        #if forced:
        #    return {"action": forced, "private_thought": f"gotta get to appointment", "memory_write": None}

        # light memory retrieval (queries could also come from LLM)
        rel = []
        for q in ("today","schedule","rent","meal","work"):
            for m in self.memory.recall(q, k=1):
                rel.append(f"[{now_str(m.t,start_dt)}] {m.kind}: {m.text}")

        env_obs = json.dumps(self.obs_list)
        roster = ", ".join(sorted(a.persona.name for a in world._agents)) if hasattr(world, "_agents") else "NEARBY"
        prompt = (
            f"You are {self.persona.name} (job: {self.persona.job}, city: {self.persona.city}) Bio: {self.persona.bio}.\n"
            f"Time {now_str(tick,start_dt)}. Location {self.place}. Mood {self.physio.mood}.\n"
            f"Needs: energy={self.physio.energy:.2f}, hunger={self.physio.hunger:.2f}, stress={self.physio.stress:.2f}.\n"
            "Recent memories:\n" + ("\n".join(rel) if rel else "(none)") + "\n"
            f"Known people: {roster}\n\n"
            f"Observation: {obs_text}, {env_obs}\n\n"
            f"My values: {', '.join(self.persona.values)}.\n"
            f"My goals: {', '.join(self.persona.goals)}.\n\n"
            "Choose ONE action and a private thought ≤20 words.\n"
            "DSL examples:\n"
            '  MOVE({"to":"Cafe"}) \n'
            '  INTERACT({"verb":"buy","item":"coffee"}) \n'
            '  THINK({"note":"private"}) \n'
            '  PLAN({"steps":["MOVE:Office","WORK:focus","EAT:Cafe"]}) \n'
            '  SAY({"to":"NEARBY","text":"..."}) \n'
            '  SLEEP()\n  EAT()\n  WORK() \n\n'
            "Return ONLY JSON with keys: action, private_thought, memory_write (nullable).\n"
            "example: {\"action\":\"SAY({'to':'NEARBY','text':'hello'})\",\"private_thought\":\"I feel happy.\",\"memory_write\":\"I said hello to someone.\"}\n"
            "Rules:\n"
            '- ALL speech or verbal communication MUST use SAY({"to":...,"text":...}) \n'
            "- INTERACT is ONLY for non-verbal actions (e.g., buy, hug, give, take, etc.), NOT for speech. \n"
            "- MOVE.to must be an existing PLACE, not an object.\n"
            "- Prefer EAT only if hunger > 0.45 and at most once per 45 minutes.\n"
            "- If unsure who to address, use SAY to NEARBY or ALL.\n"
        )
        self.obs_list = []
        out = llm.chat_json(prompt, system=BELIEF_LOCK_SYSTEM, max_tokens=256)
        # sanity carve
        if not isinstance(out, dict):
            out = {"action":"THINK()","private_thought":None,"memory_write":None}
        return out

    def act(self, world: World, decision: Dict[str,Any], tick:int):
        action = normalize_action(decision.get("action",""))
        if action.startswith("invalid action format"):
            retries = 0
            while retries < 3 and action.startswith("invalid action format"):
                fixedaction = llm.chat(f"Please correct this action call it acceptions json. \n {decision.get('action','')}", system=BELIEF_LOCK_SYSTEM, max_tokens=64)
                action = normalize_action(decision.get("action",""))
                if not action.startswith("invalid action format"):
                    break
                retries += 1

        priv   = decision.get("private_thought")
        memw   = decision.get("memory_write")


        # busy silence
        if action.startswith("CONTINUE"):
            self._homeostasis(action)
            return

        # route if needed
        if action.startswith("WORK") and not self._work_allowed_here(world):
            target = JOB_SITE.get(self.persona.job, "Office")
            action = f'MOVE({{"to":"{target}"}})'
        if action.startswith("EAT") and not self._eat_allowed_here(world):
            action = 'MOVE({"to":"Cafe"})'

        # diary
        if priv: self._maybe_write_diary(priv, tick)
        if memw and isinstance(memw, str) and memw.strip():
            self.memory.write(MemoryItem(t=tick, kind="episodic", text=memw.strip(), importance=0.6))

        # enact
        if action.startswith("SAY"):
            if (tick - self._last_say_tick) >= 6:
                world.broadcast(self.place, {"actor":self.persona.name, "kind":"say", "text":action, "t":tick})
                for agent in world._agents:
                    if agent != self:
                        out = {"agentsay": {"name": self.persona.name, "to":action, "text":action}}
                        agent.add_observation(json.dumps(out))
                self._last_say_tick = tick

        elif action.startswith("MOVE"):
            try:
                payload = json.loads(action[action.find("(")+1:action.rfind(")")])
                dest = payload.get("to")
                if dest and world.valid_place(dest) and dest != self.place:
                    self.busy_until = tick + 2
                    world.broadcast(self.place, {"actor":self.persona.name, "kind":"move", "text":action, "t":tick})

                    self.place = dest
            except Exception:
                pass

        elif action.startswith("WORK"):
            world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":"WORK()", "t":tick})
            self.busy_until = tick + 3

        elif action.startswith("EAT"):
            # cooldown behavior omitted for brevity—broadcast simple eat
            world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":"EAT()", "t":tick})
            self.busy_until = tick + 2

        elif action.startswith("PLAN"):
            world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":"PLAN", "t":tick})
            # naive plan store
            try:
                payload = json.loads(action[action.find("(")+1:action.rfind(")")]) or {}
                steps = payload.get("steps") if isinstance(payload.get("steps"), list) else []
                if steps: self.plan = steps
            except Exception:
                pass

        else:
            world.broadcast(self.place, {"actor":self.persona.name, "kind":"act", "text":action, "t":tick})

        self._homeostasis(action)

    def _homeostasis(self, action:str):
        a = action.strip()
        # passive drift
        self.physio.energy = max(0.0, self.physio.energy - 0.02)
        self.physio.hunger = min(1.0, self.physio.hunger + 0.02)
        self.physio.stress = min(1.0, self.physio.stress + 0.01)
        if a.startswith("SLEEP"):
            self.physio.energy = min(1.0, self.physio.energy + 0.5)
            self.physio.stress = max(0.0, self.physio.stress - 0.1)
        self.physio.mood = "cheerful" if (self.physio.stress < 0.3 and self.physio.energy > 0.5) else "neutral"
