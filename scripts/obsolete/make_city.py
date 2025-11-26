"""
Functional Purpose: Generates city data, places, and personas for simulation.
Description: Uses LLM and city/place modules to create city structure and populate with personas.
Replaced by: entity_creation.py (consolidated)
"""
from __future__ import annotations
import argparse, yaml, json
from typing import Optional
from sim.llm.llm_ollama import llm
from sim.world import city
from sim.world.place import GetRolesForPlace
import random
import time





def ensure_rng(rng):
    return rng if rng is not None else random

def load_names():
    with open("configs/names.yaml", "r", encoding="utf-8") as f:
        names_data = yaml.safe_load(f)
    return names_data.get("first_names", []), names_data.get("last_names", [])

def add_personas_for_places(places, cityname, start_year, used_names, seed, first_names, last_names, rng, protopersonas, progress_tracker=None):
    for place in places:
        roles = place.get('roles', [])
        if not roles:
            continue
        role_count = len(roles)
        place_persona_count = 0
        for role in roles:
            retries = 0
            while retries < 5:
                role_name = role[0] if isinstance(role, tuple) else role
                proto = GenerateProtoPersona(cityname, start_year, f"- The person's details should align with their role at the place '{place['name']}'", list(used_names), seed, first_names=first_names, last_names=last_names, rng=rng)
                if proto and 'name' in proto:
                    used_names.add(proto['name'])
                    protopersonas.append(proto)
                    print(f"[make_city] Generated persona {proto['name']} for {place['name']} | Role: {role_name}")
                    place_persona_count += 1
                    retries = 0
                    break
                else:
                    retries += 1
            if progress_tracker is not None:
                progress_tracker['done'] += 1
                percent = int(progress_tracker['done']/progress_tracker['total']*100) if progress_tracker['total'] else 100
                print(f"[make_city] {progress_tracker['done']}/{progress_tracker['total']} sub-tasks complete | Aggregated Progress: {percent}%")

def pre_stage(cityname: str = "Lumière", start_year: int = 1900, seed: int = 42, rng=None, total_steps=3, current_step=1) -> dict:

    import os
    rng = ensure_rng(rng)
    config_path = "configs/city_default_place_roles.yaml"
    protopersonas = []
    used_names = set()
    first_names, last_names = load_names()
    t0 = time.time()  # Start timing for default places

    # Try to load default places and roles from config file
    if os.path.exists(config_path):
        print(f"[make_city] Loading default places and roles from {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            default_places = yaml.safe_load(f)
        city_data = {"places": default_places}
    else:
        print(f"[make_city] Generating default places and roles and saving to {config_path}")
        city_data = city.generate_default_places(cityname, start_year)
        places = city_data.get("places", [])
        t1 = time.time()  # End timing for loading default places
        # Save roles in each place so we don't have to call GetRolesForPlace again
        for place in places:
            print(f"[role_gen] Generating roles for place '{place['name']}':{place['category']} in year {start_year}")
            place_roles = GetRolesForPlace(place.get('purpose', place['category']), year=start_year)
            place['roles'] = place_roles if place_roles else []
            print(f"[role_gen] Assigned {len(place['roles'])} roles to place '{place['name']}'")
        # Save to config file
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(places, f, allow_unicode=True, sort_keys=False)
            print(f"[make_city] Saved default places and roles to {config_path}")
        except Exception as e:
            print(f"[ERROR] Failed to write default places and roles to {config_path}: {e}")
        t2 = time.time()  # End timing for saving default places
        print(f"[timing] Default places step took {t2-t0:.2f} seconds.")

    places = city_data.get("places", [])
    total_places = len(places)
    total_roles = sum(len(place.get('roles', [])) for place in places)
    progress_tracker = {'done': 0, 'total': total_places + total_roles}
    for idx, place in enumerate(places):
        progress_tracker['done'] += 1
    add_personas_for_places(places, cityname, start_year, used_names, seed, first_names, last_names, rng, protopersonas, progress_tracker)
    print(f"[make_city] Generated {len(protopersonas)} unique protopersonas for default places in {cityname} in {start_year}")
    city_data['people'] = protopersonas

    t3 = time.time()  # Start timing for businesses
    businesses = GenerateBusinessesForCity(cityname, start_year, city_data.get("places", []), list(used_names), seed, num_businesses=30, rng=rng)
    print(f"[make_city] Generated {len(businesses)} unique business places for {cityname} in {start_year}")
    # Save roles in each business place
    for biz in businesses:
        biz_roles = GetRolesForPlace(biz.get('purpose', biz.get('category')))
        biz['roles'] = biz_roles if biz_roles else []
        print(f"[role_gen] Assigned {len(biz['roles'])} roles to business '{biz['name']}'")
    city_data['places'].extend(businesses)
    total_business_places = len(businesses)
    total_business_roles = sum(len(biz['roles']) for biz in businesses)
    progress_tracker['total'] += total_business_places + total_business_roles
    for idx, biz in enumerate(businesses):
        progress_tracker['done'] += 1
    add_personas_for_places(businesses, cityname, start_year, used_names, seed, first_names, last_names, rng, protopersonas, progress_tracker)
    print(f"[make_city] Total generated personas: {len(protopersonas)} for {cityname} in {start_year}")
    city_data['people'] = protopersonas
    t4 = time.time()  # End timing for businesses
    print(f"[timing] Businesses step took {t4-t3:.2f} seconds.")
    return city_data


def main_stage(city_data: dict, cityname: str = "Lumière", start_year: int = 1900, seed: int = 42, rng=None, total_steps=3, current_step=2) -> None:
    rng = ensure_rng(rng)
    street_names = get_street_names(num_streets=10, city=cityname, start_year=start_year, seed=seed, rng=rng)
    city_data['streets'] = street_names
    houses, street_house_counts = generate_houses(city_data.get('people', []), city_data.get('streets', []), rng)
    city_data['houses'] = houses
    city_data['street_house_counts'] = street_house_counts
    house_lookup = {h['resident']: h['address'] for h in city_data['houses']}
    for person in city_data.get('people', []):
        person['workplace'] = person.get('start_place')
        person['job_title'] = person.get('job')
        person['residence_address'] = house_lookup.get(person.get('name'))


def post_stage(city_data: dict, out: str = "configs/city.yaml", rng=None, total_steps=3, current_step=3) -> None:
    rng = ensure_rng(rng)
    valid_places = []
    seen_names = set()
    for place in city_data.get('places', []):
        if isinstance(place, dict) and 'name' in place:
            name = place['name']
            if name not in seen_names:
                valid_places.append(place)
                seen_names.add(name)
    city_data['places'] = valid_places

    streets = city_data.get('streets', [])
    places = city_data.get('places', [])
    houses = city_data.get('houses', [])
    connections = []
    for i, street in enumerate(streets):
        others = [s for j, s in enumerate(streets) if j != i]
        connected = rng.sample(others, min(2, len(others))) if others else []
        for s2 in connected:
            if [street, s2] not in connections and [s2, street] not in connections:
                connections.append([street, s2])
    for house in houses:
        address = house.get('address', '')
        parts = address.split(' ', 1)
        if len(parts) == 2:
            street = parts[1]
            if street in streets:
                connections.append([house['id'], street])
    for place in places:
        place_name = place.get('name')
        person = next((p for p in city_data.get('people', []) if p.get('workplace') == place_name), None)
        street = None
        if person:
            addr = person.get('residence_address', '')
            parts = addr.split(' ', 1)
            if len(parts) == 2 and parts[1] in streets:
                street = parts[1]
        if not street:
            street = rng.choice(streets) if streets else None
        if street:
            connections.append([place_name, street])
    city_data['connections'] = connections
    city_data['street_lengths'] = {street: count * 10 for street, count in city_data.get('street_house_counts', {}).items()}

    try:
        with open(out, "w", encoding="utf-8") as f:
            yaml.safe_dump(city_data, f, allow_unicode=True, sort_keys=False)
        print(f"Wrote {len(city_data.get('places',[]))} places, {len(city_data.get('houses',[]))} houses, {len(city_data.get('streets',[]))} streets, {len(city_data.get('connections',[]))} connections, and {len(city_data.get('people',[]))} protopersonas to {out}")
    except Exception as e:
        print(f"[ERROR] Failed to write city data to {out}: {e}")

def get_street_names(num_streets: int, city: str, start_year: int, seed: Optional[int] = None, rng=None) -> list:
    if rng is None:
        rng = random

    street_prompt = f"""
    Generate {num_streets} unique, creative, and realistic street names for the city of {city} in the year {start_year}.  Use a mix of local nature, history, and culture for names. Return ONLY a JSON object: {{"names": ["...", ...]}}
    """
    llm_seed = seed if seed is not None else rng.randint(-5000,5000)
    street_names = llm.chat_json(street_prompt, system="Return strict JSON only.", seed=llm_seed).get("names", [])
    #fall back
    if not street_names or not isinstance(street_names, list):
        street_names = [f"Oakwood Lane", "Riverbend Avenue", "Sunset Boulevard", "Maple Grove Road", "Willow Way", "Cedar Court", "Pinecrest Drive", "Elm Street"][:num_streets]
    return street_names

def GenerateBusinessesForCity(city: str, year: int, existing_places: list, restricted_names: list[str], seed: int, num_businesses: int = 10, rng=None) -> list:
    if rng is None:
        rng = random
    system_prompt = (
        "You are an expert city planner. You always return valid JSON and never any extra text. "
        "Your job is to generate lists of unique, realistic business places for a city and year. "
        "Each business must have a name, category (e.g., restaurant, shop, service), and a brief description (1-2 sentences). "
        "Avoid duplicating any existing place names already present in the city. "
        "Exclude any names provided."
    )
    user_prompt = (
        f"Generate a list of {num_businesses} unique and realistic business places for the city of {city} in the year {year}. "
        f"Exclude these names: {json.dumps(restricted_names)}. "
        "Return ONLY a JSON array in the following format: "
        "[\n  {\"name\": \"Business Name\", \"category\": \"Category\", \"description\": \"Brief description.\"}, ...\n]"
    )
    llm_seed = seed if seed is not None else rng.randint(-5000,5000)
    businesses = llm.chat_json(user_prompt, system=system_prompt, seed=llm_seed,max_tokens=2000, timeout=120).get("businesses", [])
    if not businesses or not isinstance(businesses, list):
        businesses = []
    # Filter out duplicates based on existing places
    existing_names = {place['name'].lower() for place in existing_places if 'name' in place}
    unique_businesses = []
    for biz in businesses:
        if isinstance(biz, dict) and 'name' in biz and biz['name'].lower() not in existing_names:
            unique_businesses.append(biz)
            existing_names.add(biz['name'].lower())
        if len(unique_businesses) >= num_businesses:
            break
    return unique_businesses

def GenerateProtoPersonaForPlace(city: str, year: int, place: str, role:str, restricted_names:list[str] , seed: int, rng=None) -> dict:
    if rng is None:
        rng = random
    extraguidance = f"- The person's details should align with their role at the place '{place}'"
    protoPersona = GenerateProtoPersona(city, year, extraguidance, restricted_names, seed, rng)
    protoPersona['job'] = role
    protoPersona['start_place'] = place
    return protoPersona

def GenerateProtoPersona(city: str, year: int, extraguidance:str, restricted_names:list, seed: int, first_names=None, last_names=None, rng=None) -> dict:
    if rng is None:
        rng = random
    # Draw a unique name from the provided first and last name lists, matching sex
    name = None
    sex = rng.choice(["male", "female"])
    # Ensure first_names is a list
    if not first_names:
        first_names = []
    # Try to load gendered first names if available
    if first_names and isinstance(first_names[0], dict):
        first_names_male = [n for n in first_names if isinstance(n, dict) and n.get("sex") == "male" and n["name"] not in restricted_names]
        first_names_female = [n for n in first_names if isinstance(n, dict) and n.get("sex") == "female" and n["name"] not in restricted_names]
    else:
        first_names_male = [n for n in first_names if n not in restricted_names]
        first_names_female = [n for n in first_names if n not in restricted_names]
    available_last = [n for n in last_names if n not in restricted_names] if last_names else []
    if sex == "male":
        available_first = first_names_male
    else:
        available_first = first_names_female
    if available_first and available_last:
        first = rng.choice(available_first)
        if isinstance(first, dict):
            first_name = first["name"]
        else:
            first_name = first
        last = rng.choice(available_last)
        name = f"{first_name} {last}"
        #print(f"[DEBUG] Selected name: {name} (sex: {sex})")
        restricted_names.append(first_name)
        restricted_names.append(last)
    # Choose age from a normal distribution with mean 32, stddev 12, clipped to 5-70
    age = int(max(5, min(70, rng.normalvariate(32, 12))))
    prompt = f"""You are an expert personality and character designer. Your task is to create a detailed persona for a resident of the city of {city} in the year {year}. The persona must include:
    - Age: {age}
    - Sex: {sex}
    - A realistic job for a small city in that time period.
    - A short bio (5-10 words) reflecting their job, age, and personality.
    - A list of 3 values that are important to them.
    - A list of 3 goals they are striving to achieve.
    {extraguidance}
    exclude names: {json.dumps(restricted_names)}
    The persona should be believable and fit within the historical context of the specified year. Return ONLY a JSON object in the following format:
    {{
       "age": 30,
       "sex": "{sex}",
       "job": "blacksmith",
       "bio": "Skilled craftsman; values tradition.",
       "values": ["honesty", "hard work", "community"],
       "goals": ["expand business", "learn new techniques", "support family"],
       "start_place": "Blacksmith Shop"
    }}
    Make sure the details are consistent and appropriate for the year {year}.
    """
    persona = {}
    personaupdate = llm.chat_json(prompt, system="Return strict JSON only.", seed=seed)
    persona["name"] = name
    persona["sex"] = sex
    persona.update(personaupdate if personaupdate else {})
    return persona


def generate_houses(people: list, street_names: list, rng=None):
    if rng is None:
        rng = random
    houses = []
    street_house_counts = {street: 0 for street in street_names}
    for idx, person in enumerate(people):
        street = rng.choice(street_names)
        street_house_counts[street] += 1
        house_number = street_house_counts[street] * 10
        full_name = person.get("name", f"Person {idx+1}")
        last_name = full_name.split()[-1] if " " in full_name else full_name
        house = {
            "id": f"{last_name} residence",
            "address": f"{house_number} {street}",
            "resident": full_name
        }
        houses.append(house)
    return houses, street_house_counts

# Query LLM for city details and place descriptions
def get_city_details(city: str, places: list, people: list) -> Optional[dict]:
    # Generate creative street names using LLM
    num_streets = max(3, min(8, len(people)//3))
    # LLM for places and city overview
    start_year = 1900  # Default year if not specified
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
    seed=0
    llm_seed2 = seed if seed is not None else random.randint(-5000,5000)
    result = llm.chat_json(prompt, system="Return strict JSON only.", seed=llm_seed2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a city in stages.")
    parser.add_argument('--city', default='Lumière')
    parser.add_argument('--start_year', type=int, default=1900)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--city_out', default='configs/city.yaml')
    args = parser.parse_args()
    total_start = time.time()  # Start total timing

    rng = random.Random(args.seed)
    total_steps = 3
    print(f"[make_city] Starting city generation for {args.city} in year {args.start_year} with seed {args.seed}.")
    city_data = pre_stage(cityname=args.city, start_year=args.start_year, seed=args.seed, rng=rng, total_steps=total_steps, current_step=1)
    main_stage(city_data, cityname=args.city, start_year=args.start_year, seed=args.seed, rng=rng, total_steps=total_steps, current_step=2)
    post_stage(city_data, out=args.city_out, rng=rng, total_steps=total_steps, current_step=3)
    total_end = time.time()  # End total timing
    print(f"[timing] Total city generation took {total_end-total_start:.2f} seconds.")
    print("[make_city] City generation complete.")

