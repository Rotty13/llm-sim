"""
agent_cli.py

CLI tool for creating, deleting, and managing agents (personas) in worlds for llm-sim.

Usage:
    python scripts/agent_cli.py add --world DebugWorld --name TestAgent --job None
    python scripts/agent_cli.py delete --world DebugWorld --name TestAgent
    python scripts/agent_cli.py list --world DebugWorld

This script modifies the personas.yaml file in the specified world directory.

Key Functions:
- add_agent: Add a new agent/persona to a world
- delete_agent: Remove an agent/persona from a world
- list_agents: List all agents/personas in a world

LLM Usage: None
CLI Arguments: See usage above
"""
import argparse
import os
import yaml

WORLDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'worlds')


def get_personas_path(world_name):
    return os.path.join(WORLDS_DIR, world_name, 'personas.yaml')


def load_personas(path):
    if not os.path.exists(path):
        return {'people': []}
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    if 'people' not in data:
        data['people'] = []
    return data


def save_personas(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def add_agent(world, name, job):
    path = get_personas_path(world)
    data = load_personas(path)
    if any(p.get('name') == name for p in data['people']):
        print(f"Agent '{name}' already exists in world '{world}'.")
        return
    persona = {
        'name': name,
        'job': job,
        'values': ['curiosity'],
        'goals': ['exploration'],
        'traits': {'extraversion': 0.5, 'openness': 0.5, 'conscientiousness': 0.5}
    }
    data['people'].append(persona)
    save_personas(path, data)
    print(f"Agent '{name}' added to world '{world}'.")


def delete_agent(world, name):
    path = get_personas_path(world)
    data = load_personas(path)
    before = len(data['people'])
    data['people'] = [p for p in data['people'] if p.get('name') != name]
    after = len(data['people'])
    save_personas(path, data)
    if before == after:
        print(f"Agent '{name}' not found in world '{world}'.")
    else:
        print(f"Agent '{name}' deleted from world '{world}'.")


def list_agents(world):
    path = get_personas_path(world)
    data = load_personas(path)
    if not data['people']:
        print(f"No agents found in world '{world}'.")
        return
    print(f"Agents in world '{world}':")
    for p in data['people']:
        print(f"- {p.get('name')} (job: {p.get('job')})")


def main():
    parser = argparse.ArgumentParser(description='Manage agents in llm-sim worlds.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    add_parser = subparsers.add_parser('add', help='Add a new agent to a world')
    add_parser.add_argument('--world', required=True, help='World name')
    add_parser.add_argument('--name', required=True, help='Agent name')
    add_parser.add_argument('--job', default='unemployed', help='Agent job')

    del_parser = subparsers.add_parser('delete', help='Delete an agent from a world')
    del_parser.add_argument('--world', required=True, help='World name')
    del_parser.add_argument('--name', required=True, help='Agent name')

    list_parser = subparsers.add_parser('list', help='List all agents in a world')
    list_parser.add_argument('--world', required=True, help='World name')

    args = parser.parse_args()
    if args.command == 'add':
        add_agent(args.world, args.name, args.job)
    elif args.command == 'delete':
        delete_agent(args.world, args.name)
    elif args.command == 'list':
        list_agents(args.world)

if __name__ == '__main__':
    main()
