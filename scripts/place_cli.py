"""
place_cli.py

CLI tool for creating, deleting, and managing places in worlds for llm-sim.

Usage:
    python scripts/place_cli.py add --world DebugWorld --name Park --capabilities food relax
    python scripts/place_cli.py delete --world DebugWorld --name Park
    python scripts/place_cli.py list --world DebugWorld

This script modifies the places.yaml file in the specified world directory.

Key Functions:
- add_place: Add a new place to a world
- delete_place: Remove a place from a world
- list_places: List all places in a world

LLM Usage: None
CLI Arguments: See usage above
"""

import argparse
import os
import yaml

WORLDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'worlds')

def get_city_path(world_name):
    return os.path.join(WORLDS_DIR, world_name, 'city.yaml')

def load_city(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    return data

def save_city(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

def add_place(world, name, capabilities):
    path = get_city_path(world)
    data = load_city(path)
    if 'places' not in data or data['places'] is None:
        data['places'] = []
    if any(p.get('name') == name for p in data['places']):
        print(f"Place '{name}' already exists in world '{world}'.")
        return
    place = {
        'name': name,
        'capabilities': capabilities
    }
    data['places'].append(place)
    save_city(path, data)
    print(f"Place '{name}' added to world '{world}' with capabilities: {capabilities}")

def delete_place(world, name):
    path = get_city_path(world)
    data = load_city(path)
    if 'places' not in data or data['places'] is None:
        data['places'] = []
    before = len(data['places'])
    data['places'] = [p for p in data['places'] if p.get('name') != name]
    after = len(data['places'])
    save_city(path, data)
    if before == after:
        print(f"Place '{name}' not found in world '{world}'.")
    else:
        print(f"Place '{name}' deleted from world '{world}'.")

def list_places(world):
    path = get_city_path(world)
    data = load_city(path)
    if 'places' not in data or not data['places']:
        print(f"No places found in world '{world}'.")
        return
    print(f"Places in world '{world}':")
    for p in data['places']:
        print(f"- {p.get('name')} (capabilities: {p.get('capabilities')})")

def main():
    parser = argparse.ArgumentParser(description='Manage places in llm-sim worlds.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    add_parser = subparsers.add_parser('add', help='Add a new place to a world')
    add_parser.add_argument('--world', required=True, help='World name')
    add_parser.add_argument('--name', required=True, help='Place name')
    add_parser.add_argument('--capabilities', nargs='+', default=[], help='Place capabilities (space-separated)')

    del_parser = subparsers.add_parser('delete', help='Delete a place from a world')
    del_parser.add_argument('--world', required=True, help='World name')
    del_parser.add_argument('--name', required=True, help='Place name')

    list_parser = subparsers.add_parser('list', help='List all places in a world')
    list_parser.add_argument('--world', required=True, help='World name')

    args = parser.parse_args()
    if args.command == 'add':
        add_place(args.world, args.name, args.capabilities)
    elif args.command == 'delete':
        delete_place(args.world, args.name)
    elif args.command == 'list':
        list_places(args.world)

if __name__ == '__main__':
    main()
