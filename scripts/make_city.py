from __future__ import annotations
import argparse, yaml, json
from typing import Optional
from sim.llm.llm import llm
import random

# Utility to extract places from personas.yaml

def extract_places_and_people(personas_path: str):
    with open(personas_path, "r") as f:
        data = yaml.safe_load(f)
    people = data.get("people", [])
    # Sensible default locations with city-specific names and time period appropriateness
    import inspect
    frame = inspect.currentframe()
    if frame is not None and frame.f_back is not None:
        city_name = frame.f_back.f_locals.get('city', 'Redwood')
        start_year = frame.f_back.f_locals.get('start_year', 1900)
    else:
        city_name = 'Redwood'
        start_year = 1900
    # Choose defaults based on time period
    if start_year < 1850:
        default_locations = [
            f"{city_name} Town Hall", f"{city_name} Market Square", f"{city_name} Church", f"{city_name} Blacksmith Shop", f"{city_name} Schoolhouse",
            f"{city_name} General Store", f"{city_name} Bakery", f"{city_name} Tavern", f"{city_name} Stables", f"{city_name} Apothecary"
        ]
    elif start_year < 1920:
        default_locations = [
            f"{city_name} City Hall", f"{city_name} Central Park", f"{city_name} Library", f"{city_name} General Hospital", f"{city_name} Elementary School",
            f"{city_name} Police Station", f"{city_name} Community Center", f"{city_name} Main Bakery", f"{city_name} Restaurant", f"{city_name} Public Bath"
        ]
    else:
        default_locations = [
            f"{city_name} City Hall", f"{city_name} Central Park", f"{city_name} Library", f"{city_name} General Hospital", f"{city_name} Elementary School",
            f"{city_name} Police Station", f"{city_name} Community Center", f"{city_name} Main Bakery", f"{city_name} Popular Restaurant", f"{city_name} Public Pool"
        ]
    places = [p.get("start_place") for p in people if p.get("start_place")]
    # Remove duplicates, preserve order, and combine with defaults
    seen = set()
    unique_places = []
    for place in default_locations + places:
        if place and place not in seen:
            unique_places.append(place)
            seen.add(place)
    print("[DEBUG] Extracted places (default + personas):")
    for place in unique_places:
        print(f"  - {place}")
    print("[DEBUG] People:")
    for person in people:
        print(f"  - {person['name']} ({person['job']}) @ {person.get('start_place','?')}")
    return unique_places, people


# Query LLM for city details and place descriptions
def get_city_details(city: str, places: list, people: list) -> Optional[dict]:
    # Generate creative street names using LLM
    num_streets = max(3, min(8, len(people)//3))
    def get_city_details(city: str, places: list, people: list, start_year: int = 1900, seed=None) -> dict:
        num_streets = max(3, min(8, len(people)//3))
        if seed is not None:
            random.seed(seed)
        street_prompt = f"""
    Generate {num_streets} unique, creative, and realistic street names for the city of {city} in the year {start_year}. Avoid generic names like 'Main Street' or numbers. Use a mix of local nature, history, and culture. Return ONLY a JSON object: {{"names": ["...", ...]}}
    """
        llm_seed = seed if seed is not None else random.randint(-5000,5000)
        street_names = llm.chat_json(street_prompt, system="Return strict JSON only.", seed=llm_seed).get("names", [])
        if not street_names or not isinstance(street_names, list):
            street_names = [f"Oakwood Lane", "Riverbend Avenue", "Sunset Boulevard", "Maple Grove Road", "Willow Way", "Cedar Court", "Pinecrest Drive", "Elm Street"][:num_streets]

        # Generate houses for people
        houses = []
        for idx, person in enumerate(people):
            street = street_names[idx % len(street_names)]
            house_num = 100 + idx
            house = {
                "owner": person["name"],
                "address": f"{house_num} {street}",
                "street": street,
                "person_ref": person
            }
            houses.append(house)

        print("[DEBUG] Generated houses:")
        for house in houses:
            print(f"  - {house['address']} (owner: {house['owner']})")

        # LLM for places and city overview
        prompt = f"""
    You are a city planner for the city of {city} in the year {start_year}. Here is a list of notable places:
    {json.dumps(places, indent=2)}

    For each place and an additional ten, provide a short, vivid description (1-2 sentences) and categorize it (e.g. restaurant, school, hospital, etc). Also, give a brief overview of the city (2-3 sentences). All descriptions and context should respect the historical setting of the year {start_year}.
    Return ONLY JSON in the following format:
    {{
      "city": "{city}",
      "overview": "...",
      "places": [
        {{"name": "...", "category": "...", "description": "..."}},
        ...
      ]
    }}
    """
        llm_seed2 = seed if seed is not None else random.randint(-5000,5000)
        result = llm.chat_json(prompt, system="Return strict JSON only.", seed=llm_seed2)
        # Log and save raw LLM output for debugging
        import yaml
        with open("llm_city_raw_output.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(result, f)
        print("[DEBUG] Saved raw LLM city output to llm_city_raw_output.yaml")
        # fallback if LLM fails
        if not result or "places" not in result:
            result = {
                "city": city,
                "overview": f"{city} is a vibrant small city.",
                "places": [
                    {"name": p, "category": "unknown", "description": f"A notable location in {city}."} for p in places
                ]
            }
        # Add houses and streets to city data
        result["houses"] = houses
        result["streets"] = street_names
        # Add a central node for city connectivity
        result["central_node"] = f"{city} Center"
        return result

def make_city(personas_path="configs/personas.yaml", city="Redwood", out="configs/city.yaml"):
    places, people = extract_places_and_people(personas_path)
    debug_log_path = "data/logs/city_debug.log"
    with open(debug_log_path, "a", encoding="utf-8") as dbg:
        dbg.write(f"[DEBUG make_city] places: {places}\n")
        dbg.write(f"[DEBUG make_city] people: {people}\n")
    print(f"[DEBUG make_city] places: {places}")
    print(f"[DEBUG make_city] people: {people}")

    city_data = None
    max_retries = 100
    for attempt in range(max_retries):
        city_data = get_city_details(city, places, people)
        with open(debug_log_path, "a", encoding="utf-8") as dbg:
            dbg.write(f"[DEBUG make_city] city_data (attempt {attempt+1}): {city_data}\n")
        print(f"[DEBUG make_city] city_data (attempt {attempt+1}): {city_data}")
        if city_data is not None and city_data.get('places'):
            break
    if city_data is None or not city_data.get('places'):
        # Fallback only after 100 failed attempts
        city_data = {
            "city": city,
            "overview": f"{city} is a vibrant small city.",
            "places": [
                {"name": p, "category": "unknown", "description": f"A notable location in {city}."} for p in places
            ],
            "houses": [],
            "streets": []
        }
        print(f"[WARNING] LLM failed after {max_retries} attempts. Using fallback data.")

    # Filter out malformed place entries (missing 'name') and remove duplicates by name
    valid_places = []
    seen_names = set()
    for place in city_data.get('places', []):
        if isinstance(place, dict) and 'name' in place:
            name = place['name']
            if name not in seen_names:
                valid_places.append(place)
                seen_names.add(name)
            else:
                print(f"[WARNING] Duplicate place skipped: {name}")
        else:
            print(f"[WARNING] Skipping malformed place entry: {place}")
    city_data['places'] = valid_places

    # --- Add realistic, always-connected city graph ---
    import random
    place_names = [p['name'] for p in city_data['places'] if 'name' in p]
    n = len(place_names)
    connections = []
    if n > 1:
        # Create a random spanning tree for connectivity
        nodes = place_names.copy()
        random.shuffle(nodes)
        for i in range(1, n):
            a = nodes[i]
            b = random.choice(nodes[:i])
            connections.append([a, b])
        # Add extra random edges for realism
        extra_edges = max(1, n // 3)
        for _ in range(extra_edges):
            a, b = random.sample(place_names, 2)
            if [a, b] not in connections and [b, a] not in connections:
                connections.append([a, b])
    city_data['connections'] = connections

    yaml.safe_dump(city_data, open(out, "w"), sort_keys=False)
    print(f"Wrote {len(city_data.get('places',[]))} places, {len(city_data.get('houses',[]))} houses, {len(city_data.get('streets',[]))} streets, and {len(city_data.get('connections',[]))} connections to {out}")
