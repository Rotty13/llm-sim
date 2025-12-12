"""
world_cli.py

Command-line tool for managing simulation worlds in the llm-sim project.
Supports creating, listing, deleting, showing info, and running worlds.

Usage examples:
    python scripts/world_cli.py list
    python scripts/world_cli.py info World_0
    python scripts/world_cli.py create World_1 --city "New City" --year 2025
    python scripts/world_cli.py delete World_1
    python scripts/world_cli.py run World_0 --ticks 100
"""
import argparse
import sys
from sim.world.world_manager import WorldManager

wm = WorldManager()

def cmd_list(args):
    worlds = wm.list_worlds()
    print("Available worlds:")
    for w in worlds:
        print(f"- {w}")

def cmd_info(args):
    world = args.world
    print(f"Info for world: {world}")
    city = wm.load_city(world)
    personas = wm.load_personas(world)
    names = wm.load_names(world)
    logs = wm.list_logs(world)
    print(f"City config: {bool(city)}")
    print(f"Personas: {len(personas) if personas else 0}")
    print(f"Names: {len(names) if names else 0}")

    print(f"Logs: {len(logs)} files")

def cmd_create(args):
    world = args.world
    city = args.city if hasattr(args, 'city') else None
    year = args.year if hasattr(args, 'year') else None
    try:
        wm.create_world(world, city=city, year=year)
        print(f"World '{world}' created successfully.")
    except Exception as e:
        print(f"Error creating world '{world}': {e}")

def cmd_delete(args):
    world = args.world
    confirm = input(f"Are you sure you want to delete world '{world}'? This action cannot be undone. Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("Delete operation cancelled.")
        return
    try:
        wm.delete_world(world)
        print(f"World '{world}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting world '{world}': {e}")

def cmd_run(args):
    world = args.world
    ticks = args.ticks if hasattr(args, 'ticks') else 100
    try:
        wm.run_world(world, ticks=ticks)
        print(f"World '{world}' simulation run for {ticks} ticks.")
    except Exception as e:
        print(f"Error running world '{world}': {e}")

def main():
    parser = argparse.ArgumentParser(description="World management CLI for llm-sim.")
    subparsers = parser.add_subparsers(dest="command")

    sp_list = subparsers.add_parser("list", help="List all available worlds.")
    sp_list.set_defaults(func=cmd_list)

    sp_info = subparsers.add_parser("info", help="Show info for a world.")
    sp_info.add_argument("world", help="World name")
    sp_info.set_defaults(func=cmd_info)


    sp_create = subparsers.add_parser("create", help="Create a new world.")
    sp_create.add_argument("world", help="World name")
    sp_create.add_argument("--city", help="City name", default=None)
    sp_create.add_argument("--year", type=int, help="Year", default=None)
    sp_create.set_defaults(func=cmd_create)

    sp_delete = subparsers.add_parser("delete", help="Delete a world.")
    sp_delete.add_argument("world", help="World name")
    sp_delete.set_defaults(func=cmd_delete)

    sp_run = subparsers.add_parser("run", help="Run simulation for a world.")
    sp_run.add_argument("world", help="World name")
    sp_run.add_argument("--ticks", type=int, help="Number of simulation ticks", default=100)
    sp_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
