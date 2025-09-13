from __future__ import annotations
import argparse, yaml, json
import datetime
from sim.llm.llm_ollama import llm
import random
import math
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

TEMPLATE = """
Create 5 believable residents of {city}. Return ONLY JSON Example:{{"people":[
  {{"name":"Alice Nguyen","age":28,"job":"barista","bio":"Rents a studio; loves latte art.",
    "values":["kindness","creativity","stability"],"goals":["pay rent","make friends","improve latte art"],
    "start_place":"Apartment"}}
]}}
Rules:
- Ages 18-70. Jobs realistic to a small city. start_place must be consistent and specific/unique named.
"""
TEMPLATE2 = """
Create 5 believable residents of {city} in the year {year}. Return ONLY JSON Example:{"people":[
  {"name":"Alice Nguyen","age":28,"job":"barista","bio":"Rents a studio; loves latte art.",
    "values":["kindness","creativity","stability"],"goals":["pay rent","make friends","improve latte art"],
    "start_place":"Apartment"}]
}
Rules:
- Ages 18-70. Jobs realistic to a small city and the year {year}. start_place must be consistent and specific/unique named.
- Each person must have a unique name, job, and start_place. 
- Bios should be 5-10 words, and reflect the person's job, age, and personality.
- Values and goals should be distinct and reflect the person's personality and circumstances.
"""


def make_personas(city, n=20, out="configs/personas.yaml", seed=None, places=None):
  print(f"[make_personas] Using city: {city}")
  # Load start_year from world.yaml if available
  import yaml, os
  world_yaml_path = "configs/world.yaml"
  start_year = 1900
  if os.path.exists(world_yaml_path):
    with open(world_yaml_path, "r", encoding="utf-8") as f:
      world_data = yaml.safe_load(f) or {}
      start_year = world_data.get("start_year", 1900)

  max_runs = math.ceil(n / 5.0) + 100
  people = []
  runs = 0
  # Sensible default locations
  default_locations = [
    f"{city} City Hall", f"{city} Central Park", f"{city} Library", f"{city} General Hospital", f"{city} Elementary School",
    f"{city} Police Station", f"{city} Community Center", f"{city} Main Bakery", f"{city} Popular Restaurant", f"{city} Public Pool"
  ]
  if seed is not None:
    random.seed(seed)
  available_places = places if places else default_locations
  used_places = set()
  while len(people) < n and runs < max_runs:
    prompt = f"""
Create 5 believable residents of {city} in the year {start_year}. Return ONLY JSON Example:{{"people":[
  {{"name":"Alice Nguyen","age":28,"job":"barista","bio":"Rents a studio; loves latte art.",
    "values":["kindness","creativity","stability"],"goals":["pay rent","make friends","improve latte art"],
    "start_place":"Apartment"}}
]}}
Rules:
- Ages 18-70. Jobs realistic to a small city and the year {start_year}. start_place must be consistent and specific/unique named.
- Each person must have a unique name, job, and start_place.
- Bios should be 5-10 words, and reflect the person's job, age, and personality.
- Values and goals should be distinct and reflect the person's personality and circumstances.
All details should respect the historical context of the year {start_year}.
"""
    chat_seed = seed if seed is not None else 1
    data = llm.chat_json(prompt, system="Return strict JSON only.", seed=chat_seed)
    newpeople = data.get("people", [])
    # Assign unique start_place from available_places
    for person in newpeople:
      if not person.get("start_place") or person["start_place"] in used_places:
        available_unique = [p for p in available_places if p not in used_places]
        if available_unique:
          person["start_place"] = random.choice(available_unique)
          used_places.add(person["start_place"])
        else:
          person["start_place"] = random.choice(default_locations)
      else:
        used_places.add(person["start_place"])
    people.extend(newpeople)
    runs += 1
  # Truncate to requested number
  with open(out, "w", encoding="utf-8") as f:
    yaml.safe_dump({"people": people[:n]}, f, allow_unicode=True, sort_keys=False)
  print(f"Wrote {len(people[:n])} personas to {out}")


if __name__ == "__main__":
  import datetime
  parser = argparse.ArgumentParser(description="Generate personas for a city.")
  parser.add_argument("--city", type=str, default="Lumière", help="Name of the city.")
  parser.add_argument("--n", type=int, default=20, help="Number of personas to generate.")
  parser.add_argument("--out", type=str, default="configs/personas.yaml", help="Output YAML file for personas.")
  parser.add_argument("--seed", type=int, default=int(datetime.datetime.now().timestamp()), help="Random seed for reproducibility.")
  parser.add_argument("--places", type=str, nargs='*', default=["house1", "house2"], help="List of places in the city to assign as start_place.")
  args = parser.parse_args()
  make_personas(args.city, args.n, args.out, args.seed, args.places)