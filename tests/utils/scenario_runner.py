"""
scenario_runner.py

Utility to load a scenario YAML and initialize a world and agents for testing.
"""
import yaml
import os
from sim.agents.agents import Agent, Persona, Physio
from sim.world.world import World, Place


def load_scenario(scenario_path):
    with open(scenario_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    world_data = data['world']
    from sim.inventory.inventory import ITEMS
    places = {}
    for p in world_data['places']:
        place = Place(
            name=p['name'],
            neighbors=p.get('neighbors', []),
            capabilities=set(p.get('capabilities', [])),
            purpose=p.get('purpose', '')
        )
        # Load inventory if present
        for item in p.get('inventory', []):
            item_id = item['item_id']
            qty = item.get('qty', 1)
            if item_id in ITEMS:
                place.inventory.add(ITEMS[item_id], qty)
        places[p['name']] = place
    world = World(places=places, name=world_data['name'])
    agents = []
    for a in data['agents']:
        persona = Persona(
            name=a['name'],
            age=a.get('age', 30),
            city=a.get('city', 'TestCity'),
            bio=a.get('bio', ''),
            job=a.get('job', 'unemployed'),
            values=a.get('values', []),
            goals=a.get('goals', []),
            traits=a.get('traits', {})
        )
        physio = Physio(**a.get('physio', {}))
        agent = Agent(persona=persona, physio=physio, place=a.get('place', None))
        agents.append(agent)
        world.add_agent(agent)
    return world, agents
