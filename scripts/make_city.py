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

    def add_personas_for_places(places,  stage_name="pre_stage", progress_tracker=None):
        total_roles = 0
        for place in places:
            roles = GetRolesForPlace(place.get('purpose',place['category']))
            if roles:
                total_roles += len(roles)
       
        for place in places:
            roles = GetRolesForPlace(place.get('purpose',place['category']))
            if not roles:
                continue
            role_count = len(roles)
            place_persona_count = 0
            for role in roles:
                retries:int =0
                while retries < 5 and place_persona_count < role_count:
                    role_name = role[0] if isinstance(role, tuple) else role
                    proto = GenerateProtoPersona(cityname, start_year, f"- The person's details should align with their role at the place '{place['name']}'", list(used_names), seed, first_names=first_names, last_names=last_names, rng=rng)
                    if proto and 'name' in proto:
                        used_names.add(proto['name'])
                        protopersonas.append(proto)
                        place_persona_count += 1
                        retries = 0
                        print(f"[DEBUG] Generated persona: {proto['name']} - {proto.get('job','N/A')}, age {proto.get('age','N/A')} | Progress: {place_persona_count}/{role_count}")
                    else:
                        retries += 1
                        print(f"[WARNING] Failed to generate persona for role '{role_name}' at place '{place['name']}' (retry {retries}/5)")
                if place_persona_count < role_count:
                    print(f"[WARNING] Not all personas generated for place '{place['name']}' (generated {place_persona_count}/{role_count})")

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
        placeroles = GetRolesForPlace(place.get('purpose',place['category']))
        if placeroles:
            total_roles += len(placeroles)
    # We'll count protopersonas as the same as total_roles
    # For businesses, we add after
    progress_tracker = {'done': 0, 'total': total_places + total_roles}
    # Place generation progress
    for idx, place in enumerate(places):
        progress_tracker['done'] += 1
        percent = int(progress_tracker['done']/progress_tracker['total']*100) if progress_tracker['total'] else 100
        print(f"[AGG_PROGRESS] Place {idx+1}/{total_places} generated | Aggregated Progress: {percent}%")
    # Protopersona generation progress
    add_personas_for_places(places, stage_name="pre_stage", progress_tracker=progress_tracker)
    city_data['people'] = protopersonas
    print(f"[pre_stage] Generated default places and personas for {cityname}. Total places: {len(city_data.get('places',[]))} Total personas: {len(protopersonas)} | Aggregated Progress: {int(progress_tracker['done']/progress_tracker['total']*100) if progress_tracker['total'] else 100}%")

    # Generate businesses and add personas for them
    businesses = GenerateBusinessesForCity(cityname, start_year, city_data.get("places", []), list(used_names), seed, num_businesses=30, rng=rng)
    city_data['places'].extend(businesses)
    # Add business places and personas to progress
    total_business_places = len(businesses)
    total_business_roles = 0
    for biz in businesses:
        placeroles = GetRolesForPlace(biz['category'])
        if placeroles:
            total_business_roles += len(placeroles)
    progress_tracker['total'] += total_business_places + total_business_roles
    for idx, biz in enumerate(businesses):
        progress_tracker['done'] += 1
        percent = int(progress_tracker['done']/progress_tracker['total']*100) if progress_tracker['total'] else 100
        print(f"[AGG_PROGRESS] Business Place {idx+1}/{total_business_places} generated | Aggregated Progress: {percent}%")
    add_personas_for_places(businesses, stage_name="business_personas", progress_tracker=progress_tracker)
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
    #city_data['houses'] = generate_houses(city_data.get('people', []), city_data.get('streets', []), rng)
    houses, street_house_counts = generate_houses(city_data.get('people', []), city_data.get('streets', []), rng)
    city_data['houses'] = houses
    city_data['street_house_counts'] = street_house_counts
    print(f"[main_stage] Generated houses for personas in {cityname}. Total houses: {len(city_data.get('houses',[]))} | Progress: {int(current_step/total_steps*100)}%")

    # Add workplace, job_title, and residence_address to each persona
    # Build lookup for houses by resident name
    house_lookup = {h['resident']: h['address'] for h in city_data['houses']}
    for person in city_data.get('people', []):
        # Workplace: use start_place if present, else None
        person['workplace'] = person.get('start_place')
        # Job title: use job if present, else None
        person['job_title'] = person.get('job')
        # Residence address: lookup by name
        person['residence_address'] = house_lookup.get(person.get('name'))
   

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

    # --- Add realistic city graph: streets connect to streets, places/houses connect to their street ---
    streets = city_data.get('streets', [])
    places = city_data.get('places', [])
    houses = city_data.get('houses', [])
    connections = []
    # Connect each street to 1-2 other streets
    for i, street in enumerate(streets):
        others = [s for j, s in enumerate(streets) if j != i]
        connected = rng.sample(others, min(2, len(others))) if others else []
        for s2 in connected:
            if [street, s2] not in connections and [s2, street] not in connections:
                connections.append([street, s2])
    # Connect each house to its street
    for house in houses:
        address = house.get('address', '')
        parts = address.split(' ', 1)
        if len(parts) == 2:
            street = parts[1]
            if street in streets:
                connections.append([house['id'], street])
    # Connect each place to a street (if possible)
    for place in places:
        place_name = place.get('name')
        # Find a person who works at this place
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
        print(f"Wrote {len(city_data.get('places',[]))} places, {len(city_data.get('houses',[]))} houses, {len(city_data.get('streets',[]))} streets, {len(city_data.get('connections',[]))} connections, and {len(city_data.get('people',[]))} protopersonas to {out} | Progress: {int((current_step-0.5)/total_steps*100)}%")
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

