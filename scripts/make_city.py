from __future__ import annotations
import argparse, yaml, json
from typing import Optional
from sim.llm.llm import llm
from sim.world import city
from sim.world.place import GetRolesForPlace
import random




def pre_stage(cityname: str = "Lumière", start_year: int = 1900, seed: int = 42, rng=None, total_steps=3, current_step=1) -> dict:
    if rng is None:
        rng = random
    city_data = city.generate_default_places(cityname, start_year)
    protopersonas = []
    used_names = set()

    # Load name pools from configs/names.yaml
    with open("configs/names.yaml", "r", encoding="utf-8") as f:
        names_data = yaml.safe_load(f)
        first_names = names_data.get("first_names", [])
        last_names = names_data.get("last_names", [])

    def add_personas_for_places(places, role_key, stage_name="pre_stage", progress_tracker=None):
        total_roles = 0
        for place in places:
            roles = GetRolesForPlace(place[role_key])
            if roles:
                total_roles += len(roles)
        persona_count = 0
        for place in places:
            roles = GetRolesForPlace(place[role_key])
            if not roles:
                continue
            for role in roles:
                role_name = role[0] if isinstance(role, tuple) else role
                proto = GenerateProtoPersona(cityname, start_year, f"- The person's details should align with their role at the place '{place['name']}'", list(used_names), seed, first_names=first_names, last_names=last_names, rng=rng)
                if proto and 'name' in proto:
                    used_names.add(proto['name'])
                    protopersonas.append(proto)
                persona_count += 1
                if progress_tracker is not None:
                    progress_tracker['done'] += 1
                    percent = int(progress_tracker['done']/progress_tracker['total']*100) if progress_tracker['total'] else 100
                    print(f"[AGG_PROGRESS] {progress_tracker['done']}/{progress_tracker['total']} sub-tasks complete | Aggregated Progress: {percent}%")

    # Add personas for default places
    # Aggregate progress: places, roles, protopersonas
    places = city_data.get("places", [])
    total_places = len(places)
    total_roles = 0
    for place in places:
        roles = GetRolesForPlace(place['role'])
        if roles:
            total_roles += len(roles)
    # We'll count protopersonas as the same as total_roles
    # For businesses, we add after
    progress_tracker = {'done': 0, 'total': total_places + total_roles}
    # Place generation progress
    for idx, place in enumerate(places):
        progress_tracker['done'] += 1
        percent = int(progress_tracker['done']/progress_tracker['total']*100) if progress_tracker['total'] else 100
        print(f"[AGG_PROGRESS] Place {idx+1}/{total_places} generated | Aggregated Progress: {percent}%")
    # Protopersona generation progress
    add_personas_for_places(places, 'role', stage_name="pre_stage", progress_tracker=progress_tracker)
    city_data['people'] = protopersonas
    print(f"[pre_stage] Generated default places and personas for {cityname}. Total places: {len(city_data.get('places',[]))} Total personas: {len(protopersonas)} | Aggregated Progress: {int(progress_tracker['done']/progress_tracker['total']*100) if progress_tracker['total'] else 100}%")

    # Generate businesses and add personas for them
    businesses = GenerateBusinessesForCity(cityname, start_year, city_data.get("places", []), list(used_names), seed, num_businesses=10, rng=rng)
    city_data['places'].extend(businesses)
    # Add business places and personas to progress
    total_business_places = len(businesses)
    total_business_roles = 0
    for biz in businesses:
        roles = GetRolesForPlace(biz['category'])
        if roles:
            total_business_roles += len(roles)
    progress_tracker['total'] += total_business_places + total_business_roles
    for idx, biz in enumerate(businesses):
        progress_tracker['done'] += 1
        percent = int(progress_tracker['done']/progress_tracker['total']*100) if progress_tracker['total'] else 100
        print(f"[AGG_PROGRESS] Business Place {idx+1}/{total_business_places} generated | Aggregated Progress: {percent}%")
    add_personas_for_places(businesses, 'category', stage_name="business_personas", progress_tracker=progress_tracker)
    city_data['people'] = protopersonas
    print(f"[pre_stage] Added businesses and personas for {cityname}. Total places: {len(city_data.get('places',[]))} Total personas: {len(protopersonas)} | Aggregated Progress: {int(progress_tracker['done']/progress_tracker['total']*100) if progress_tracker['total'] else 100}%")
    return city_data

def main_stage(city_data: dict, cityname: str = "Lumière", start_year: int = 1900, seed: int = 42, rng=None, total_steps=3, current_step=2) -> None:
    if rng is None:
        rng = random

    # generate streets and houses for the protopeople in citydata
    street_names = get_street_names(num_streets=10, city=cityname, start_year=start_year, seed=seed, rng=rng)
    print(f"[main_stage] Generated street names for {cityname}: {street_names} | Progress: {int((current_step-0.5)/total_steps*100)}%")
    city_data['streets'] = street_names

    # Generate houses for the protopeople in city_data
    city_data['houses'] = generate_houses(city_data.get('people', []), city_data.get('streets', []), rng)
    print(f"[main_stage] Generated houses for personas in {cityname}. Total houses: {len(city_data.get('houses',[]))} | Progress: {int(current_step/total_steps*100)}%")
   

def post_stage(city_data: dict, out: str = "configs/city.yaml", rng=None, total_steps=3, current_step=3) -> None:
    if rng is None:
        rng = random
    # Finalize city using personas and write output
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
    place_names = [p['name'] for p in city_data['places'] if 'name' in p]
    n = len(place_names)
    connections = []
    if n > 1:
        nodes = place_names.copy()
        rng.shuffle(nodes)
        for i in range(1, n):
            a = nodes[i]
            b = rng.choice(nodes[:i])
            connections.append([a, b])
        extra_edges = max(1, n // 3)
        for _ in range(extra_edges):
            a, b = rng.sample(place_names, 2)
            if [a, b] not in connections and [b, a] not in connections:
                connections.append([a, b])
    city_data['connections'] = connections

    try:
        with open(out, "w", encoding="utf-8") as f:
            yaml.safe_dump(city_data, f, allow_unicode=True, sort_keys=False)
        print(f"Wrote {len(city_data.get('places',[]))} places, {len(city_data.get('houses',[]))} houses, {len(city_data.get('streets',[]))} streets, and {len(city_data.get('connections',[]))} connections to {out} | Progress: {int((current_step-0.5)/total_steps*100)}%")
        print(f"[post_stage] Finalized city and wrote to {out}. | Progress: {int(current_step/total_steps*100)}%")
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
    prompt = f"""
    You are an expert city planner for the city of {city} in the year {year}. Your task is to generate a list of {num_businesses} unique and realistic business places that would fit well within the historical context of the city. Each business should have a name, category (e.g., restaurant, shop, service), and a brief description (1-2 sentences). Avoid duplicating any existing place names or categories already present in the city. Exclude names: {json.dumps(restricted_names)}. Return ONLY a JSON array in the following format:
    [
      {{"name": "Business Name", "category": "Category", "description": "Brief description."}},
      ...
    ]
    """
    llm_seed = seed if seed is not None else rng.randint(-5000,5000)
    businesses = llm.chat_json(prompt, system="Return strict JSON only.", seed=llm_seed)
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
        print(f"[DEBUG] Selected name: {name} (sex: {sex})")
        restricted_names.append(first_name)
        restricted_names.append(last)
    prompt = f"""You are an expert personality and character designer. Your task is to create a detailed persona for a resident of the city of {city} in the year {year}. The persona must include:
    - An age between 5 and 70.
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
    print(f"[DEBUG] Generated persona: {persona}")
    return persona



def generate_houses(people: list, street_names: list, rng=None) -> list:
    if rng is None:
        rng = random
    houses = []
    for idx, person in enumerate(people):
        street = rng.choice(street_names)
        house_number = rng.randint(1, 200)
        house = {
            "id": f"house_{idx+1}",
            "address": f"{house_number} {street}",
            "resident": person.get("name", f"Person {idx+1}")
        }
        houses.append(house)
    return houses

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
    parser.add_argument('--personas_out', default='configs/personas.yaml')
    parser.add_argument('--city_out', default='configs/city.yaml')
    args = parser.parse_args()


    print(f"[make_city] Starting city generation for {args.city} in year {args.start_year} with seed {args.seed}. | Progress: 0%")

    rng = random.Random(args.seed)
    total_steps = 3

    # Step 1: Pre-stage: Generate government places and people, then their houses
    print(f"[make_city] Pre-stage... | Progress: {int(1/total_steps*100)}%")
    city_data = pre_stage(cityname=args.city, start_year=args.start_year, seed=args.seed, rng=rng, total_steps=total_steps, current_step=1)

    # Step 2: Main-stage: Generate businesses, people for businesses, and their houses
    print(f"[make_city] Main-stage... | Progress: {int(2/total_steps*100)}%")
    try:
        main_stage(city_data, cityname=args.city, start_year=args.start_year, seed=args.seed, rng=rng, total_steps=total_steps, current_step=2)
    except NotImplementedError as nie:
        print(f"[make_city] {nie}")

    # Step 3: Post-stage: Finalize city and write output
    print(f"[make_city] Post-stage... | Progress: {int(3/total_steps*100)}%")
    post_stage(city_data, out=args.city_out, rng=rng, total_steps=total_steps, current_step=3)

    print("[make_city] City generation complete. | Progress: 100%")

