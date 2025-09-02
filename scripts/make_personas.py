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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", default="Redwood")
    ap.add_argument("-n", type=int, default=20)
    ap.add_argument("--out", default="configs/personas.yaml")
    args = ap.parse_args()
    runs:int=math.ceil(args.n / 5.0)
    people:list=list()
    runs = 0
    while len(people)<args.n or runs>args.n+100:
      prompt = TEMPLATE2.format(city=args.city)
      data = llm.chat_json(prompt, system="Return strict JSON only.", seed=random.randint(-5000,5000))
      newpeople=data.get("people", [])
      people.extend(newpeople)
      runs+=1
    
    yaml.safe_dump({"people": people[:args.n-1]}, open(args.out, "w"), sort_keys=False)
    print(f"Wrote {len(people)} personas to {args.out}")

if __name__ == "__main__":
    main()
