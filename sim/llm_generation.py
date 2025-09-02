# LLM-based generation functions and helpers
from typing import List, Dict, Any
from .llm import OllamaClient
from .world import Place, Vendor, World

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
    # ...implementation from sim_ollama2_old.py...
    return {}

def llm_generate_personas(num_agents:int=4, city_name:str="Redwood", place_names:List[str]=None) -> List:
    # ...implementation from sim_ollama2_old.py...
    return []

def build_world_from_llm(num_places=6, city="Redwood") -> World:
    # ...implementation from sim_ollama2_old.py...
    from .world import World, Place
    return World(places={"Dummy": Place(name="Dummy", neighbors=[], capabilities=set())})

def spawn_agents_from_llm(world:World, num_agents=4, seed_money=20) -> List:
    # ...implementation from sim_ollama2_old.py...
    return []
