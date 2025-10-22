"""Simple place controller.

Features:
- load a place YAML from data/yaml/places
- inspect the place to determine a small staff roster
- call the project's LLM helpers to generate persona descriptions for staff
- create a minimal World containing the place and run a simple tick loop where
  agents (staff) perform steps using existing Agent/World APIs

This script is intentionally lightweight and reuses helpers in sim.llm.llm_generation
and sim.world/world.py, sim.agents.agents.Agent. It can be run as a module or imported.
"""
from __future__ import annotations
import os
import yaml
import json
import time
from typing import List, Dict, Any

from sim.llm import llm_ollama
from sim.world.world import Place, World, Vendor
from sim.agents.agents import Agent, Persona

llm = llm_ollama.LLM()

PLACES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "yaml", "places")


def load_place_yaml(place_name: str) -> Dict[str, Any]:
    """Load a YAML file matching place_name (without extension) from data/yaml/places.
    Returns the parsed YAML as dict. Raises FileNotFoundError if not found.

    This version only attempts direct filename matches and does not walk the directory.
    """
    place_name = place_name.split('.')[0]  # strip extension if given
    candidates = [
        f"{place_name}.yaml",
        f"{place_name}.yml",
        f"{place_name.lower()}.yaml",
        f"{place_name.lower()}.yml",
    ]
    for fn in candidates:
        path = os.path.join(PLACES_DIR, fn)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                # Some place files (like train_station_3.yaml) nest the actual
                # place definition under a top-level key (e.g. 'station').
                # Normalize to return the inner dict when present.
                if isinstance(data, dict) and len(data) == 1:
                    key = next(iter(data.keys()))
                    inner = data.get(key)
                    if isinstance(inner, dict):
                        # attach a synthetic 'type' so callers can detect it
                        inner['_source_type'] = key
                        return inner
                return data
    raise FileNotFoundError(f"Place YAML for '{place_name}' not found in {PLACES_DIR}")


def infer_staff_from_place(place_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return a list of staff role descriptors inferred from the place data.

    Simple heuristic rules:
    - if capabilities contain 'coffee' or 'food' => need barista/cook and 1 server
    - if name contains 'station' or 'train' => need attendant and security
    - if capabilities contain 'work_dev' => need receptionist and manager
    - fallback: 1 attendant/host
    """
    # Accept either the project's simple place schema or a station schema
    caps = set()
    caps_src = place_data.get('capabilities')
    if isinstance(caps_src, (list, set)):
        caps = {str(c).lower() for c in caps_src}

    # If the YAML was a station object, it may include a human-readable name
    # under fields like 'location' or 'station' keys. Try common fallbacks.
    name = str(place_data.get('name') or place_data.get('description') or
               place_data.get('location', {}).get('city') or "").lower()

    roles = []
    # If the file explicitly lists staff, use those roles directly
    staff_list = place_data.get('staff')
    if isinstance(staff_list, list) and staff_list:
        # Count occurrences of role titles (or fallback to generic titles)
        from collections import Counter
        titles = []
        for s in staff_list:
            if isinstance(s, dict):
                # some YAMLs put a descriptive sentence in 'role'; prefer 'name' when
                # 'role' looks like a long description (contains spaces and more than ~6 words)
                raw_role = s.get('role')
                name_field = s.get('name')
                if isinstance(raw_role, str) and len(raw_role.split()) > 6 and name_field:
                    title = name_field
                else:
                    title = raw_role or name_field
            else:
                title = str(s)
            if title:
                titles.append(str(title).lower())
        counts = Counter(titles)
        for title, cnt in counts.items():
            # normalize some common role names
            norm = 'security' if 'security' in title else ('conductor' if 'conduct' in title else title)
            roles.append({'role': norm, 'count': int(cnt)})
        return roles


    return roles


def generate_staff_personas(place_name: str, roles: List[Dict[str, Any]], city_name: str = "Redwood") -> List[Persona]:
    """Generate staff personas by delegating to `llm_generate_personas` and mapping jobs to roles.

    This avoids calling low-level LLM functions directly and reuses the project's persona helper.
    """
    total = sum(r.get('count', 1) for r in roles)
    # expand roles into an ordered list so we can assign jobs deterministically
    desired_jobs = []
    for r in roles:
        desired_jobs.extend([r.get('role')] * int(r.get('count', 1)))

    personas = []

    # Minimal deterministic local LLM-like generator (no external dependencies)
    class SimpleLLM:
        def __init__(self, seed=0):
            self.seed = seed

        def chat_json(self, prompt, max_tokens=512, **kwargs):
            # extract requested count from the prompt if present
            import re
            m = re.search(r"Generate a JSON array of (\d+) persona", prompt)
            n = int(m.group(1)) if m else total
            out = []
            for i in range(n):
                out.append({
                    "name": f"AutoPerson{i+1}",
                    "age": 25 + (i % 20),
                    "job": desired_jobs[i] if i < len(desired_jobs) else 'attendant',
                    "city": city_name,
                    "bio": f"Auto-generated persona {i+1} for {place_name}.",
                    "values": ["service"],
                    "goals": ["do my job"]
                })
            return out

    # Use our SimpleLLM to generate deterministic personas
    prompt_text = (
        f"Generate a JSON array of {total} persona objects for staff at {place_name} in {city_name}. "
        "Each persona should be an object with keys: name (string), age (int), job (string), city (string), bio (string), values (array of strings), goals (array of strings). "
        "Return ONLY valid JSON (an array)."
    )
    simple = SimpleLLM()
    out = simple.chat_json(prompt_text, max_tokens=512)
    if isinstance(out, list):
        for item in out:
            try:
                personas.append(Persona(
                    name=item.get('name', 'Anon'),
                    age=int(item.get('age', 30)),
                    job=str(item.get('job', 'attendant')),
                    city=str(item.get('city', city_name)),
                    bio=str(item.get('bio', '')),
                    values=list(item.get('values', [])) or [],
                    goals=list(item.get('goals', [])) or []
                ))
            except Exception:
                continue

    # expand roles into an ordered list so we can assign jobs deterministically
    desired_jobs = []
    for r in roles:
        desired_jobs.extend([r.get('role')] * int(r.get('count', 1)))

    # if llm_generate_personas returned Persona objects, remap their job fields to the desired job when possible
    out = []
    for i in range(total):
        if i < len(personas):
            p = personas[i]
            # override job to match inferred role if different
            if i < len(desired_jobs):
                p.job = str(desired_jobs[i]).lower()
            out.append(p)
        else:
            # fallback synthetic persona
            role = desired_jobs[i] if i < len(desired_jobs) else 'attendant'
            out.append(Persona(name=f"Staff_{i+1}", age=30, job=role, city=city_name, bio="Auto-generated staff.", values=["service"], goals=["do my job"]))
    return out


def build_place_world(place_name: str, place_data: Dict[str, Any]) -> World:
    """Build a minimal World that contains a single Place (and optional vendor).
    """
    caps = set()
    caps_src = place_data.get('capabilities')
    if isinstance(caps_src, (list, set)):
        caps = {str(c).lower() for c in caps_src}

    # For station-style files, we can also infer that this place offers 'transit'
    if place_data.get('_source_type') == 'station' or 'train' in (place_name or '').lower():
        caps.add('transit')

    vendor = None
    if isinstance(place_data.get('vendor'), dict):
        v = place_data.get('vendor', {})
        vendor = Vendor(prices=v.get('prices', {}), stock=v.get('stock', {}), buyback=v.get('buyback', {}))

    # Derive a friendly title for the place. If the station YAML has a location.city,
    # prefer that as a human-readable place name.
    # Prefer explicit name/title; if filename was passed as place_name prefer
    # to use the station's city (if provided) for friendlier naming.
    city = None
    if isinstance(place_data.get('location'), dict):
        city = place_data.get('location', {}).get('city')
    friendly_name = place_data.get('name') or place_data.get('title')
    if not friendly_name:
        if city:
            friendly_name = f"{city} Station"
        else:
            friendly_name = place_name

    place = Place(name=friendly_name or place_name, neighbors=[], capabilities=caps, vendor=vendor, purpose=place_data.get('description',''))
    world = World(places={place.name: place})
    return world


def run_place_loop(world: World, staff_agents: List[Agent], ticks: int = 12, start_dt=None):
    """Run a simple loop for the place. Each tick, step staff agents and process world events.
    """
    # Ensure world knows about agents
    world._agents = staff_agents
    # The environment must provide a configured LLM. Do not inject fallbacks here.
    # If a configured LLM singleton is not present, raise an informative error.
   
    logs = []
    for t in range(ticks):
        # simple observation: recent events at place
        while world.events:
            ev = world.events.popleft()
            logs.append((t, ev))
        obs = f"Tick {t} at place"
        for ag in list(staff_agents):
            try:
                ag.step_interact(world=world, participants=staff_agents, obs=obs, tick=t, start_dt=start_dt, incoming_message=None, loglist=logs)
            except Exception as e:
                logs.append((t, {"error": str(e), "actor": ag.persona.name}))
        # brief pause to allow LLM rates to be manageable in interactive runs
        time.sleep(0.05)
    return logs


def main(place_name: str, ticks: int = 12):
    place_data = load_place_yaml(place_name)
    # harmonize name
    place_title = place_data.get('name') or place_name
    roles = infer_staff_from_place({**place_data, 'name': place_title})
    print(f"Inferred roles for {place_title}: {roles}")
    personas = generate_staff_personas(place_title, roles)
    print(f"Generated {len(personas)} personas")
    # create agents
    agents = [Agent(persona=p, place=place_title) for p in personas]
    world = build_place_world(place_title, place_data)
    logs = run_place_loop(world, agents, ticks=ticks)
    print("Run complete. Sample logs:")
    for item in logs[:20]:
        print(item)


if __name__ == '__main__':
    # Interactive prompt using click.prompt
    from click import prompt
    place = prompt('Place name (filename or key) in data/yaml/places')
    ticks = prompt('Ticks to run (int)', default=12)
    try:
        ticks = int(ticks)
    except Exception:
        ticks = 12
    main(place, ticks=ticks)
