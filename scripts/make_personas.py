from __future__ import annotations
import argparse, yaml, json
from sim.llm.llm import llm
import random
import math

TEMPLATE = """
Create 5 believable residents of {city}. Return ONLY JSON Example:{{"people":[
  {{"name":"Alice Nguyen","age":28,"job":"barista","bio":"Rents a studio; loves latte art.",
    "values":["kindness","creativity","stability"],"goals":["pay rent","make friends","improve latte art"],
    "start_place":"Apartment"}}
]}}
Rules:
- Ages 18-70. Jobs realistic to a small city. start_place must be consistent and specific/unique named.
"""
TEMPLATE2="""
Create 5 believable residents of {city}. Return ONLY JSON Example:{{"people":[
  {{"name":"Alice Nguyen","age":28,"job":"barista","bio":"Rents a studio; loves latte art.",
    "values":["kindness","creativity","stability"],"goals":["pay rent","make friends","improve latte art"],
    "start_place":"Apartment"}}
]}}
Rules:
- Ages 18-70. Jobs realistic to a small city. start_place must be consistent and specific/unique named.
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

  runs:int=math.ceil(n / 5.0)
  people:list=list()
  runs = 0
  # Sensible default locations
  default_locations = [
    f"{city} City Hall", f"{city} Central Park", f"{city} Library", f"{city} General Hospital", f"{city} Elementary School",
    f"{city} Police Station", f"{city} Community Center", f"{city} Main Bakery", f"{city} Popular Restaurant", f"{city} Public Pool"
  ]
  if seed is not None:
    random.seed(seed)
  # Use provided places if available, else default_locations
  available_places = places if places else default_locations
  while len(people)<n and runs<n+100:
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
    llm_seed = seed if seed is not None else random.randint(-5000,5000)
    data = llm.chat_json(prompt, system="Return strict JSON only.", seed=llm_seed)
    newpeople=data.get("people", [])
    # Randomly assign some personas a start_place from available_places
    for person in newpeople:
      if not person.get("start_place") or person["start_place"] in [p["start_place"] for p in people]:
        # 50% chance to use a place from available_places
        if random.random() < 0.5:
          person["start_place"] = random.choice(available_places)
        else:
          person["start_place"] = random.choice(default_locations)
    people.extend(newpeople)
    runs+=1
  # Truncate to requested number
  yaml.safe_dump({"people": people[:n]}, open(out, "w"), sort_keys=False)
  print(f"Wrote {len(people[:n])} personas to {out}")
