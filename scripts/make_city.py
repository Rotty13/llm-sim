from __future__ import annotations
import argparse, yaml, json
from sim.llm.llm import llm
import random

# Utility to extract places from personas.yaml

def extract_places_and_people(personas_path: str):
    with open(personas_path, "r") as f:
        data = yaml.safe_load(f)
    people = data.get("people", [])
    # Sensible default locations
    default_locations = [
        "City Hall", "Central Park", "Library", "General Hospital", "Elementary School",
        "Police Station", "Community Center", "Main Bakery", "Popular Restaurant", "Public Pool"
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
def get_city_details(city: str, places: list, people: list) -> dict:
    # Generate creative street names using LLM
    num_streets = max(3, min(8, len(people)//3))
    street_prompt = f"""
Generate {num_streets} unique, creative, and realistic street names for the city of {city}. Avoid generic names like 'Main Street' or numbers. Use a mix of local nature, history, and culture. Return ONLY a JSON object: {{"names": ["...", ...]}}
"""
    street_names = llm.chat_json(street_prompt, system="Return strict JSON only.", seed=random.randint(-5000,5000)).get("names", [])
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
You are a city planner for the city of {city}. Here is a list of notable places:
{json.dumps(places, indent=2)}

For each place and an additional ten, provide a short, vivid description (1-2 sentences) and categorize it (e.g. restaurant, school, hospital, etc). Also, give a brief overview of the city (2-3 sentences).
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
    result = llm.chat_json(prompt, system="Return strict JSON only.", seed=random.randint(-5000,5000))
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
    city_data = get_city_details(city, places, people)
    # Filter out malformed place entries (missing 'name')
    valid_places = []
    for place in city_data.get('places', []):
        if isinstance(place, dict) and 'name' in place:
            valid_places.append(place)
        else:
            print(f"[WARNING] Skipping malformed place entry: {place}")
    city_data['places'] = valid_places
    yaml.safe_dump(city_data, open(out, "w"), sort_keys=False)
    print(f"Wrote {len(city_data.get('places',[]))} places, {len(city_data.get('houses',[]))} houses, and {len(city_data.get('streets',[]))} streets to {out}")
