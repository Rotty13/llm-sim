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


def make_personas(city="Redwood", n=20, out="configs/personas.yaml"):
  runs:int=math.ceil(n / 5.0)
  people:list=list()
  runs = 0
  # Sensible default locations
  default_locations = [
    f"{city} City Hall", f"{city} Central Park", f"{city} Library", f"{city} General Hospital", f"{city} Elementary School",
    f"{city} Police Station", f"{city} Community Center", f"{city} Main Bakery", f"{city} Popular Restaurant", f"{city} Public Pool"
  ]
  while len(people)<n and runs<n+100:
    prompt = TEMPLATE2.format(city=city)
    data = llm.chat_json(prompt, system="Return strict JSON only.", seed=random.randint(-5000,5000))
    newpeople=data.get("people", [])
    # Assign start_place from default_locations if missing or not unique
    for person in newpeople:
      if not person.get("start_place") or person["start_place"] in [p["start_place"] for p in people]:
        person["start_place"] = random.choice(default_locations)
    people.extend(newpeople)
    runs+=1
  # Truncate to requested number
  yaml.safe_dump({"people": people[:n]}, open(out, "w"), sort_keys=False)
  print(f"Wrote {len(people[:n])} personas to {out}")
