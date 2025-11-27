"""
world_manager.py

Provides WorldManager class for handling file I/O, data loading, and management of simulation worlds. Supports loading world configs, personas, names, and logs from compartmentalized world directories. Intended for use by other scripts to access world data in a unified way.
"""
import os
import yaml
import json
from typing import Dict, Any, Optional, List, TYPE_CHECKING
import logging
from sim.utils.schema_validation import (
    validate_city_config, validate_personas_config, validate_world_config,
    validate_names_config, validate_place_connectivity
)
from sim.scheduler.scheduler import Appointment

if TYPE_CHECKING:
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
        # Lazy imports to avoid circular dependencies
        from sim.world.world import World
        from sim.agents.agents import Agent, Persona
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
                world.add_agent(agent)
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

    def validate_config(self, world_name: str, config_type: str = "all") -> List[str]:
        """
        Validate configuration files for a world.
        Args:
            world_name (str): Name of the world.
            config_type (str): Type of config to validate ('city', 'personas', 'world', 'names', 'all').
        Returns:
            List[str]: List of validation error messages.
        """
        errors = []
        
        if config_type in ("city", "all"):
            city_data = self.load_yaml(world_name, "city.yaml")
            if city_data:
                errors.extend(validate_city_config(city_data))
                # Validate place connectivity if places exist
                if "places" in city_data and isinstance(city_data["places"], list):
                    errors.extend(validate_place_connectivity(city_data["places"]))
        
        if config_type in ("personas", "all"):
            personas_data = self.load_yaml(world_name, "personas.yaml")
            if personas_data:
                errors.extend(validate_personas_config(personas_data))
        
        if config_type in ("world", "all"):
            world_data = self.load_yaml(world_name, "world.yaml")
            if world_data:
                errors.extend(validate_world_config(world_data))
        
        if config_type in ("names", "all"):
            names_data = self.load_yaml(world_name, "names.yaml")
            if names_data:
                errors.extend(validate_names_config(names_data))
        
        return errors

    def load_places(self, world_name: str) -> Dict[str, Any]:
        """
        Load and validate places from city.yaml.
        Args:
            world_name (str): Name of the world.
        Returns:
            Dict[str, Any]: Dictionary mapping place names to Place objects.
        """
        from sim.world.world import Place, Vendor
        
        city_data = self.load_city(world_name)
        if not city_data:
            logger.warning(f"No city.yaml found for world '{world_name}'")
            return {}
        
        places_data = city_data.get("places", [])
        if not places_data:
            # Try 'features' as fallback for legacy format
            features = city_data.get("features", [])
            if features:
                # Convert features list to basic places
                places_data = [{"name": f, "neighbors": [], "capabilities": []} for f in features]
        
        places = {}
        for place_cfg in places_data:
            if not isinstance(place_cfg, dict):
                continue
            
            name = place_cfg.get("name", "")
            if not name:
                continue
            
            # Parse vendor if present
            vendor = None
            vendor_cfg = place_cfg.get("vendor")
            if vendor_cfg and isinstance(vendor_cfg, dict):
                vendor = Vendor(
                    prices=vendor_cfg.get("prices", {}),
                    stock=vendor_cfg.get("stock", {}),
                    buyback=vendor_cfg.get("buyback", {})
                )
            
            # Parse capabilities
            capabilities = set(place_cfg.get("capabilities", []))
            
            place = Place(
                name=name,
                neighbors=place_cfg.get("neighbors", []),
                capabilities=capabilities,
                vendor=vendor,
                purpose=place_cfg.get("purpose", "")
            )
            places[name] = place
        
        return places

    def load_agents_with_schedules(self, world_name: str) -> List['Agent']:
        """
        Load agents from personas.yaml with full schedule parsing and initialization.
        Args:
            world_name (str): Name of the world.
        Returns:
            List[Agent]: List of fully initialized Agent instances.
        """
        from sim.agents.agents import Agent, Persona
        
        personas_data = self.load_yaml(world_name, "personas.yaml")
        if not personas_data:
            logger.warning(f"No personas.yaml found for world '{world_name}'")
            return []
        
        # Support both 'people' and 'personas' keys
        persona_list = personas_data.get("people", personas_data.get("personas", []))
        if not persona_list:
            logger.warning(f"No personas found in personas.yaml for world '{world_name}'")
            return []
        
        agents = []
        for persona_cfg in persona_list:
            if not isinstance(persona_cfg, dict):
                continue
            
            name = persona_cfg.get("name", "")
            if not name:
                logger.warning(f"Skipping persona without name: {persona_cfg}")
                continue
            
            # Create Persona object
            persona = Persona(
                name=name,
                age=persona_cfg.get("age", 30),
                job=persona_cfg.get("job", persona_cfg.get("role", "unemployed")),
                city=persona_cfg.get("city", "unknown"),
                bio=persona_cfg.get("bio", ""),
                values=persona_cfg.get("values", persona_cfg.get("traits", [])),
                goals=persona_cfg.get("goals", [])
            )
            
            # Parse schedule into Appointment objects
            schedule_data = persona_cfg.get("schedule", [])
            calendar = []
            for entry in schedule_data:
                if isinstance(entry, dict):
                    try:
                        appt = Appointment(
                            start_tick=entry.get("start_tick", 0),
                            end_tick=entry.get("end_tick", 0),
                            location=entry.get("location", ""),
                            label=entry.get("label", "")
                        )
                        calendar.append(appt)
                    except (TypeError, KeyError) as e:
                        logger.warning(f"Invalid schedule entry for {name}: {entry}, error: {e}")
            
            # Get starting position
            position = persona_cfg.get("position", persona_cfg.get("start_place", ""))
            
            # Create Agent
            agent = Agent(
                persona=persona,
                place=position,
                calendar=calendar
            )
            
            agents.append(agent)
            logger.debug(f"Loaded agent {name} at position '{position}' with {len(calendar)} appointments")
        
        return agents

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
            valid_personas.append(persona)

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
        # Lazy import to avoid circular dependencies
        from sim.agents.agents import Agent, Persona
        
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
