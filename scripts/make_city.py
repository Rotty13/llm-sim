from __future__ import annotations
import argparse, yaml, json
from typing import Optional
from sim.llm.llm import llm
from sim.world import city
from sim.world.place import GetRolesForPlace
import random




city_data:dict
# --- Staged World Generation Functions ---
def pre_stage(cityname="Lumière", start_year=1900, seed=42):
    global city_data
    city_data = {}
    # Generate default government places based on time period
    city_data = city.generate_default_places(cityname, start_year)
    #Generate protopersonas for default places
    protopersonas = []
    used_names = set()
    for place in city_data.get("places", []):
        roles = GetRolesForPlace(place['role'])
        if not roles:
            continue
        for role in roles:
            import datetime
            seed = int(datetime.datetime.now().timestamp())
            # If role is a tuple (role, description), extract the role name
            if isinstance(role, tuple):
                role_name = role[0]
            else:
                role_name = role
            proto = GenerateProtoPersonaForPlace(cityname, start_year, place['name'], role_name, list(used_names), seed)
            if proto and 'name' in proto:
                used_names.add(proto['name'])
                protopersonas.append(proto)
            pass
    city_data['people'] = protopersonas

    print(f"[pre_stage] Generated default places and personas for {cityname}. Total places: {len(city_data.get('places',[]))} Total personas: 0")

def main_stage(cityname="Redwood", start_year=1900, seed=42):
    # Generate business places and personas (stub for now)
    # You can expand this to generate businesses and assign people
    print(f"[main_stage] Business generation for {cityname} not yet implemented.")

def post_stage(out="configs/city.yaml"):
    # Finalize city using personas and write output
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

    yaml.safe_dump(city_data, open(out, "w", encoding="utf-8"), allow_unicode=True, sort_keys=False)
    print(f"Wrote {len(city_data.get('places',[]))} places, {len(city_data.get('houses',[]))} houses, {len(city_data.get('streets',[]))} streets, and {len(city_data.get('connections',[]))} connections to {out}")
    print(f"[post_stage] Finalized city and wrote to {out}.")

def get_street_names(num_streets: int, city: str, start_year: int, seed: Optional[int] = None) -> list:
    if seed is not None:
        random.seed(seed)

    street_prompt = f"""
    Generate {num_streets} unique, creative, and realistic street names for the city of {city} in the year {start_year}.  Use a mix of local nature, history, and culture for names. Return ONLY a JSON object: {{"names": ["...", ...]}}
    """
    llm_seed = seed if seed is not None else random.randint(-5000,5000)
    street_names = llm.chat_json(street_prompt, system="Return strict JSON only.", seed=llm_seed).get("names", [])
    #fall back
    if not street_names or not isinstance(street_names, list):
        street_names = [f"Oakwood Lane", "Riverbend Avenue", "Sunset Boulevard", "Maple Grove Road", "Willow Way", "Cedar Court", "Pinecrest Drive", "Elm Street"][:num_streets]
    return street_names


def GenerateProtoPersonaForPlace(city: str, year: int, place: str, role:str, restricted_names:list[str] , seed: int) -> dict:
    extraguidance = f"- The person's details should align with their role at the place '{place}'"
    protoPersona = GenerateProtoPersona(city, year, extraguidance, restricted_names, seed)
    protoPersona['job'] = role
    protoPersona['start_place'] = place
    return protoPersona

def GenerateProtoPersona(city: str, year: int, extraguidance:str, restricted_names:list, seed: int) -> dict:
    prompt = f"""You are an expert personality and character designer. Your task is to create a detailed persona for a resident of the city of {city} in the year {year}. The persona must include:
- A unique name appropriate for the time period and location.
- An age between 5 and 70.
- A realistic job for a small city in that time period.
- A short bio (5-10 words) reflecting their job, age, and personality.
- A list of 3 values that are important to them.
- A list of 3 goals they are striving to achieve.
{extraguidance}
exclude names: {json.dumps(restricted_names)}
The persona should be believable and fit within the historical context of the specified year. Return ONLY a JSON object in the following format:
{{
  "name": "John Doe",
   "age": 30,
   "job": "blacksmith",
   "bio": "Skilled craftsman; values tradition.",
   "values": ["honesty", "hard work", "community"],
   "goals": ["expand business", "learn new techniques", "support family"],
   "start_place": "Blacksmith Shop"
}}
Make sure the details are consistent and appropriate for the year {year}.
"""
    
    persona = llm.chat_json(prompt, system="Return strict JSON only.", seed=seed)
    return persona



def generate_houses(people: list, street_names: list) -> list:
    houses = []
    for idx, person in enumerate(people):
        street = random.choice(street_names)
        house_number = random.randint(1, 200)
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


    print(f"[make_city] Starting city generation for {args.city} in year {args.start_year} with seed {args.seed}.")

    # Step 1: Pre-stage: Generate government places and people, then their houses
    print("[make_city] Pre-stage...")
    pre_stage(cityname=args.city, start_year=args.start_year, seed=args.seed)

    # Step 2: Main-stage: Generate businesses, people for businesses, and their houses
    print("[make_city] Main-stage...")
    main_stage(cityname=args.city, start_year=args.start_year, seed=args.seed)

    # Step 3: Post-stage: Finalize city and write output
    print("[make_city] Post-stage...")
    post_stage(out=args.city_out)

    print("[make_city] City generation complete.")

