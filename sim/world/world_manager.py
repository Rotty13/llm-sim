"""
world_manager.py

Provides WorldManager class for handling file I/O, data loading, and management of simulation worlds. Supports loading world configs, personas, names, and logs from compartmentalized world directories. Intended for use by other scripts to access world data in a unified way.
"""
import os
import yaml
import json
from typing import Dict, Any, Optional
import logging
from sim.agents.agents import Agent, Persona

logger = logging.getLogger(__name__)

class WorldManager:
    def create_world(self, world_name: str, city: Optional[str] = None, year: Optional[int] = None):
        """
        Create a new world directory with default config files.
        Args:
            world_name (str): Name of the world to create.
            city (Optional[str]): City name for the world.
            year (Optional[int]): Year for the world.
        Raises:
            FileExistsError: If the world already exists.
        """
        import shutil
        world_path = self.get_world_path(world_name)
        if os.path.exists(world_path):
            raise FileExistsError(f"World '{world_name}' already exists.")
        os.makedirs(world_path)
        # Create default city.yaml
        city_data = {"name": city or "New City", "year": year or 2025}
        with open(os.path.join(world_path, "city.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump(city_data, f)
        # Create default personas.yaml
        personas_data = {"people": []}
        with open(os.path.join(world_path, "personas.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump(personas_data, f)
        # Create default names.yaml
        names_data = {"names": []}
        with open(os.path.join(world_path, "names.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump(names_data, f)
        # Create default world.yaml
        world_data = {"description": f"World {world_name}", "city": city_data}
        with open(os.path.join(world_path, "world.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump(world_data, f)
        # Create conversation_logs directory
        os.makedirs(os.path.join(world_path, "conversation_logs"))

    def delete_world(self, world_name: str):
        """
        Delete a world directory and all its contents.
        Args:
            world_name (str): Name of the world to delete.
        Raises:
            FileNotFoundError: If the world does not exist.
        """
        import shutil
        world_path = self.get_world_path(world_name)
        if not os.path.exists(world_path):
            raise FileNotFoundError(f"World '{world_name}' does not exist.")
        shutil.rmtree(world_path)

    def run_world(self, world_name: str, ticks: int = 100):
        """
        Run a simulation for the given world using the simulation loop.
        Args:
            world_name (str): Name of the world to run.
            ticks (int): Number of simulation ticks to run.
        """
        print(f"Running simulation for world '{world_name}' for {ticks} ticks...")
        # Load world object and agents (stub: would need actual loading logic)
        from sim.world.world import World
        # Example: create empty world with loaded places
        city = self.load_city(world_name)
        places_data = city.get('places', {}) if city else {}
        places = {p['name']: p for p in places_data} if places_data else {}
        world = World(places=places)

        # Load agents from personas.yaml
        personas = self.load_personas(world_name)
        if personas:
            for persona_data in personas:
                # Create Persona object
                persona = Persona(
                    name=persona_data["name"],
                    age=persona_data.get("age", 0),
                    job=persona_data.get("job", "unemployed"),
                    city=persona_data.get("city", "unknown"),
                    bio=persona_data.get("bio", ""),
                    values=persona_data.get("values", []),
                    goals=persona_data.get("goals", [])
                )
                # Initialize agent with Persona and place
                agent = Agent(
                    persona=persona,
                    place=persona_data.get("position", "unknown"),
                    calendar=persona_data.get("schedule", [])
                )

                # Validate agent's position
                if agent.place not in world.places:
                    logger.warning(f"Invalid place '{agent.place}' for agent {agent.persona.name}. Assigning default place.")
                    agent.place = next(iter(world.places))  # Assign the first place as default

                # Add agent to the world
                world.add_agent(agent)
                world.set_agent_location(agent, agent.place)

        # Run simulation loop
        world.simulation_loop(ticks)
        print(f"Simulation for world '{world_name}' completed.")
    def __init__(self, worlds_dir: str = "worlds"):
        """
        Initialize WorldManager with the given worlds directory.
        Args:
            worlds_dir (str): Directory containing world folders.
        """
        self.worlds_dir = worlds_dir

    def list_worlds(self) -> list:
        """
        Return a list of available world directories.
        Returns:
            list: List of world directory names.
        """
        return [d for d in os.listdir(self.worlds_dir) if os.path.isdir(os.path.join(self.worlds_dir, d))]

    def get_world_path(self, world_name: str) -> str:
        """
        Get the absolute path to a world directory.
        Args:
            world_name (str): Name of the world.
        Returns:
            str: Absolute path to the world directory.
        """
        return os.path.join(self.worlds_dir, world_name)

    def load_yaml(self, world_name: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load a YAML file from a world directory.
        Args:
            world_name (str): Name of the world.
            filename (str): YAML filename to load.
        Returns:
            Optional[Dict[str, Any]]: Parsed YAML data or None if not found.
        """
        path = os.path.join(self.get_world_path(world_name), filename)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_json(self, world_name: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load a JSON file from a world directory.
        Args:
            world_name (str): Name of the world.
            filename (str): JSON filename to load.
        Returns:
            Optional[Dict[str, Any]]: Parsed JSON data or None if not found.
        """
        path = os.path.join(self.get_world_path(world_name), filename)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_personas(self, world_name: str) -> Optional[list]:
        """
        Load personas from a world's personas.yaml file.
        Args:
            world_name (str): Name of the world.
        Returns:
            Optional[list]: List of personas or empty list if not found.
        """
        personas = self.load_yaml(world_name, "personas.yaml")
        # Validate personas structure
        if not isinstance(personas, dict) or "people" not in personas:
            logger.warning(f"Invalid personas.yaml structure for world '{world_name}'. Expected a 'people' key.")
            return []

        valid_personas = []
        for persona in personas["people"]:
            if not all(key in persona for key in ["name", "position", "schedule"]):
                logger.warning(f"Skipping invalid persona entry: {persona}. Missing required fields.")
                continue

            # Parse and validate schedule
            schedule = persona.get("schedule", [])
            if not isinstance(schedule, list):
                logger.warning(f"Invalid schedule for persona {persona['name']}. Expected a list.")
                schedule = []

            # Validate position
            position = persona.get("position", "unknown")
            if not isinstance(position, str):
                logger.warning(f"Invalid position for persona {persona['name']}. Expected a string.")
                position = "unknown"

            # Add validated persona
            valid_personas.append({
                "name": persona["name"],
                "position": position,
                "schedule": schedule,
                "age": persona.get("age", 0),
                "job": persona.get("job", "unemployed"),
                "city": persona.get("city", "unknown"),
                "bio": persona.get("bio", ""),
                "values": persona.get("values", []),
                "goals": persona.get("goals", [])
            })

        return valid_personas

    def load_names(self, world_name: str) -> Optional[list]:
        """
        Load names from a world's names.yaml file.
        Args:
            world_name (str): Name of the world.
        Returns:
            Optional[list]: List of names or empty list if not found.
        """
        names = self.load_yaml(world_name, "names.yaml")
        if names and "names" in names:
            return names["names"]
        return [] if names is None else []

    def load_city(self, world_name: str) -> Optional[Dict[str, Any]]:
        """
        Load city configuration from a world's city.yaml file.
        Args:
            world_name (str): Name of the world.
        Returns:
            Optional[Dict[str, Any]]: City configuration or None if not found.
        """
        return self.load_yaml(world_name, "city.yaml")

    def load_world(self, world_name: str) -> Optional[Dict[str, Any]]:
        """
        Load world configuration from a world's world.yaml file.
        Args:
            world_name (str): Name of the world.
        Returns:
            Optional[Dict[str, Any]]: World configuration or None if not found.
        """
        return self.load_yaml(world_name, "world.yaml")

    def get_logs_dir(self, world_name: str) -> str:
        """
        Get the path to the conversation logs directory for a world.
        Args:
            world_name (str): Name of the world.
        Returns:
            str: Path to the logs directory.
        """
        return os.path.join(self.get_world_path(world_name), "conversation_logs")

    def list_logs(self, world_name: str) -> list:
        """
        List all log files in a world's conversation_logs directory.
        Args:
            world_name (str): Name of the world.
        Returns:
            list: List of log filenames.
        """
        logs_dir = self.get_logs_dir(world_name)
        if not os.path.exists(logs_dir):
            return []
        return [f for f in os.listdir(logs_dir) if os.path.isfile(os.path.join(logs_dir, f))]

    def load_log(self, world_name: str, log_filename: str) -> Optional[str]:
        """
        Load a specific log file from a world's conversation_logs directory.
        Args:
            world_name (str): Name of the world.
            log_filename (str): Log filename to load.
        Returns:
            Optional[str]: Log file contents or None if not found.
        """
        path = os.path.join(self.get_logs_dir(world_name), log_filename)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def load_agents(self, world_name: str):
        """
        Load agents from the personas.yaml file for the specified world.
        Args:
            world_name (str): Name of the world.
        Returns:
            list: List of Agent instances.
        """
        personas_path = os.path.join(self.get_world_path(world_name), "personas.yaml")
        with open(personas_path, 'r') as file:
            personas_data = yaml.safe_load(file).get("people", [])

        agents = []
        for persona_data in personas_data:
            persona = Persona(
                name=persona_data["name"],
                age=persona_data.get("age", 0),
                job=persona_data.get("job", "unemployed"),
                city=persona_data.get("city", "unknown"),
                bio=persona_data.get("bio", ""),
                values=persona_data.get("values", []),
                goals=persona_data.get("goals", [])
            )
            agent = Agent(
                persona=persona,
                place=persona_data.get("start_place", "unknown"),
                calendar=persona_data.get("schedule", [])
            )
            agents.append(agent)
        return agents

    def validate_config(self, world_name: str, filename: str, schema: Dict[str, Any]) -> bool:
        """
        Validate a configuration file against a schema.
        Args:
            world_name (str): Name of the world.
            filename (str): Configuration filename to validate.
            schema (Dict[str, Any]): Schema to validate against.
        Returns:
            bool: True if valid, False otherwise.
        """
        data = self.load_yaml(world_name, filename)
        if not data:
            logger.error(f"Failed to load {filename} for validation.")
            return False

        from sim.utils.schema_validation import validate_nested_schema
        if not validate_nested_schema(data, schema):
            logger.error(f"Validation failed for {filename} in world '{world_name}'.")
            return False

        logger.info(f"Validation passed for {filename} in world '{world_name}'.")
        return True

    def load_places(self, world_name: str) -> Optional[Dict[str, Any]]:
        """
        Load and validate places from a world's places.yaml file.
        Args:
            world_name (str): Name of the world.
        Returns:
            Optional[Dict[str, Any]]: Validated places data or None if invalid.
        """
        from sim.utils.schema_validation import validate_nested_schema
        schema_path = os.path.join("configs", "yaml", "schemas", "places.yaml")
        with open(schema_path, "r", encoding="utf-8") as schema_file:
            schema = yaml.safe_load(schema_file)

        if not self.validate_config(world_name, "places.yaml", schema):
            logger.error(f"Failed to validate places.yaml for world '{world_name}'.")
            return None

        return self.load_yaml(world_name, "places.yaml")
