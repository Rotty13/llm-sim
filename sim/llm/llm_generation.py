# LLM-based generation functions and helpers
from typing import List, Dict, Any
from .llm_ollama import OllamaClient
from ..world.world import Place, Vendor, World
import json
import random
from ..agents.agents import Agent, Persona, Appointment
from ..inventory.inventory import ITEMS

ALLOWED_CAPS = {
    "sleep","food_home","food","coffee","work_dev","park","shop","hospital","school","gym","bar","gallery","transit"
}

ITEMS_CATALOG = {
    "coffee": 3.5, "pastry": 4.0, "beans": 12.0, "salad": 3.0
}
ALLOWED_ITEM_IDS = set(ITEMS_CATALOG.keys())

ollama = OllamaClient()

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

def _ensure_connectivity(places: dict):
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
    for i in range(len(comps)-1):
        a = comps[i][0]; b = comps[i+1][0]
        if b not in places[a].neighbors: places[a].neighbors.append(b)
        if a not in places[b].neighbors: places[b].neighbors.append(a)

def _dedupe_neighbors(places: dict):
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

from typing import Optional
def llm_generate_personas(num_agents:int=4, city_name:str="Redwood", place_names: Optional[List[str]] = None) -> List:
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

def spawn_agents_from_llm(world:World, num_agents=4, seed_money=20) -> List:
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
