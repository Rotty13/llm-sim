import sys, os, yaml, json
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sim.llm.llm import llm

city = "Lumière"
places = [
    f"{city} City Hall", f"{city} Central Park", f"{city} Library", f"{city} General Hospital", f"{city} Elementary School",
    f"{city} Police Station", f"{city} Community Center", f"{city} Main Bakery", f"{city} Popular Restaurant", f"{city} Public Pool"
]
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

print("Testing LLM city generation prompt...")
result = llm.chat_json(prompt, system="Return strict JSON only.")
print("Raw LLM response:", result)
with open("llm_city_test_output.yaml", "w") as f:
    yaml.safe_dump(result, f)
print("LLM city response saved to llm_city_test_output.yaml")
