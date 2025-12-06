"""
world_manager.py

Provides WorldManager class for handling file I/O, data loading, and management of simulation worlds. Supports loading world configs, personas, names, and logs from compartmentalized world directories. Intended for use by other scripts to access world data in a unified way.

Key Classes:
- WorldManager: Main class for world file operations and data loading.

Key Methods:
- load_personas: Load and validate personas from personas.yaml
- load_agents: Load fully configured Agent instances
- load_city: Load city configuration with validation
- load_world: Load world configuration with validation

LLM Usage:
- None

CLI Arguments:
- None (library module)
"""
import os
import yaml
import json
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING
import logging
from sim.utils.schema_validation import (
    validate_city_config, validate_personas_config, validate_world_config,
    validate_names_config, validate_place_connectivity
)
from sim.scheduler.scheduler import Appointment

if TYPE_CHECKING:
    from sim.agents.agents import Agent, Persona

from sim.utils.logging import SimLogger
from sim.world.place import Area

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
                self.sim_logger = None  # Set per run
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
            # Logger setup is only done in run_world, not here.
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
        if self.sim_logger:
            self.sim_logger.info(f"Created new world: {world_name}", extra={"world_name": world_name, "city": city, "year": year})

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
        if self.sim_logger:
            self.sim_logger.info(f"Deleted world: {world_name}", extra={"world_name": world_name})

    def run_world(self, world_name: str, ticks: int = 100, validate: bool = True):
        """
        Run a simulation for the given world using the simulation loop.
        
        Args:
            world_name (str): Name of the world to run.
            ticks (int): Number of simulation ticks to run.
        """
        # Set session_datetime as the very first operation
        from datetime import datetime
        self.session_datetime = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        session_datetime = self.session_datetime
        from sim.utils.logging import SimLogger
        self.sim_logger = SimLogger(world_name=world_name, session_datetime=session_datetime)
        print(f"Running simulation for world '{world_name}' for {ticks} ticks...")
        # Lazy imports to avoid circular dependencies
        from sim.world.world import World, Place
        from sim.agents.agents import Agent
        from sim.agents.persona import Persona
        from sim.utils.metrics import SimulationMetrics
        if self.sim_logger:
            self.sim_logger.info(f"Simulation started: world={world_name}, ticks={ticks}", extra={"world_name": world_name, "ticks": ticks})
        city = self.load_city(world_name)
        places_data = city.get('places', []) if city else []

        # Convert place dictionaries to Place objects
        places = {}
        for place_dict in places_data:
            place = Place(
                name=place_dict['name'],
                neighbors=place_dict.get('neighbors', []),
                capabilities=set(place_dict.get('capabilities', [])),
                purpose=place_dict.get('purpose', '')
            )
            # Load areas if specified
            areas_data = place_dict.get('areas', [])
            initial_area_name = None
            for area_dict in areas_data:
                area = Area(
                    name=area_dict['name'],
                    description=area_dict.get('description', ''),
                    properties=area_dict.get('properties', {})
                )
                # Load initial inventory for area
                inventory_data = area_dict.get('inventory', {})
                for item_id, qty in inventory_data.items():
                    area.add_item(item_id, qty)
                place.add_area(area)
                if not initial_area_name:
                    initial_area_name = area.name  # First area is default
            # Store initial area name for agent placement
            place.attributes['initial_area'] = initial_area_name
            places[place.name] = place
        # Create a new SimulationMetrics instance for this run
        metrics = SimulationMetrics()
        # Create world with places and name, pass metrics instance and sim_logger
        world = World(places=places, name=world_name, metrics=metrics, sim_logger=self.sim_logger)

        # Load agents with full initialization and link to world
        agents = self.load_agents(world_name, world)
        print(f"Loaded {len(agents)} agents into world with {len(places)} places")
        # Add agents to world
        for agent in agents:
            world.add_agent(agent)

        # Run simulation loop
        world.simulation_loop(ticks)

        # Stop and export metrics after simulation loop
        metrics.stop(ticks)
        # Use the same session_datetime for output dir
        output_dir = os.path.join('outputs', world_name, session_datetime)
        os.makedirs(output_dir, exist_ok=True)
        metrics.export_json(os.path.join(output_dir, f"{world_name}_metrics.json"))

    def __init__(self, worlds_dir: str = "worlds"):
        """
        Initialize WorldManager with the given worlds directory.
        Args:
                    sim_logger.warning(f"Skipping persona without name: {persona}")
        """
        self.worlds_dir = worlds_dir
        self.sim_logger = None  # Will be set per run

    # Removed duplicate validate_config method (see below for correct version)

    # Removed duplicate load_places method (see below for correct version)

    def load_agents_with_schedules(self, world_name: str) -> List['Agent']:
        """
                    sim_logger.warning(f"Invalid position for persona {name}. Expected a string, using 'unknown'.")
        Args:
            world_name (str): Name of the world.
        Returns:
            List[Agent]: List of fully initialized Agent instances.
        """
        from sim.agents.agents import Agent
        from sim.agents.persona import Persona
        
        personas_data = self.load_yaml(world_name, "personas.yaml")
        if not personas_data:
            if self.sim_logger:
                self.sim_logger.warning(f"No personas.yaml found for world '{world_name}'")
            return []
        # Support both 'people' and 'personas' keys
        persona_list = personas_data.get("people", personas_data.get("personas", []))
        if not persona_list:
            if self.sim_logger:
                self.sim_logger.warning(f"No personas found in personas.yaml for world '{world_name}'")
            return []
        agents = []
        for persona_cfg in persona_list:
            if not isinstance(persona_cfg, dict):
                continue
            name = persona_cfg.get("name", "")
            if not name:
                if self.sim_logger:
                    self.sim_logger.warning(f"Skipping persona without name: {persona_cfg}")
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
                        if self.sim_logger:
                            self.sim_logger.warning(f"Invalid schedule entry for {name}: {entry}, error: {e}")
            position = persona_cfg.get("position", persona_cfg.get("start_place", ""))
            agent = Agent(
                persona=persona,
                place=position,
                calendar=calendar
            )
            agents.append(agent)
            if self.sim_logger:
                self.sim_logger.info(f"Agent activated: {name} at position '{position}'", extra={"agent": name, "place": position})
                self.sim_logger.debug(f"Loaded agent {name} at position '{position}' with {len(calendar)} appointments")
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

    def load_personas(self, world_name: str, validate: bool = True) -> Optional[list]:
        """
        Load personas from a world's personas.yaml file with complete schedule parsing.
        
        Args:
            world_name (str): Name of the world.
            validate (bool): Whether to validate the config against schema.
        
        Returns:
            Optional[list]: List of validated persona dictionaries or empty list if not found.
        """
        personas = self.load_yaml(world_name, "personas.yaml")
        
        # Validate structure
        if not isinstance(personas, dict):
            if self.sim_logger:
                self.sim_logger.warning(f"Invalid personas.yaml structure for world '{world_name}'. Expected dict.")
            return []
        
        # Schema validation if requested
        if validate:
            result = validate_personas_config(personas)
            if not result.is_valid:
                for error in result.errors:
                    if self.sim_logger:
                        self.sim_logger.warning(f"Validation warning: {error}")
        
        # Get people list - support both 'people' and 'personas' keys
        people_list = personas.get("people", personas.get("personas", []))
        if not isinstance(people_list, list):
            if self.sim_logger:
                self.sim_logger.warning(f"Invalid personas.yaml structure for world '{world_name}'. Expected 'people' list.")
            return []

        valid_personas = []
        for persona in people_list:
            if not isinstance(persona, dict):
                if self.sim_logger:
                    self.sim_logger.warning(f"Skipping invalid persona entry (not a dict): {persona}")
                continue
                
            # Name is required
            name = persona.get("name")
            if not name:
                if self.sim_logger:
                    self.sim_logger.warning(f"Skipping persona without name: {persona}")
                continue

            # Parse schedule - convert to Appointment objects if dict entries
            raw_schedule = persona.get("schedule", [])
            parsed_schedule = self._parse_schedule(raw_schedule, name)

            # Get position - support both 'position' and 'start_place'
            position = persona.get("position") or persona.get("start_place", "unknown")
            if not isinstance(position, str):
                if self.sim_logger:
                    self.sim_logger.warning(f"Invalid position for persona {name}. Expected a string, using 'unknown'.")
                position = "unknown"

            # Build validated persona data
            valid_personas.append({
                "name": name,
                "position": position,
                "schedule": parsed_schedule,
                "age": persona.get("age", 0),
                "job": persona.get("job", "unemployed"),
                "city": persona.get("city", "unknown"),
                "bio": persona.get("bio", ""),
                "values": persona.get("values", []),
                "goals": persona.get("goals", [])
            })

        return valid_personas

    def _parse_schedule(self, raw_schedule: Any, persona_name: str) -> List[Appointment]:
        """
        Parse a raw schedule into a list of Appointment objects.
        
        Args:
            raw_schedule: Raw schedule data (list of dicts or Appointments).
            persona_name: Name of the persona for error logging.
        
        Returns:
            List[Appointment]: Parsed schedule as Appointment objects.
        """
        if not isinstance(raw_schedule, list):
            if self.sim_logger:
                self.sim_logger.warning(f"Invalid schedule for persona {persona_name}. Expected a list.")
            return []
        
        appointments = []
        for i, entry in enumerate(raw_schedule):
            if isinstance(entry, Appointment):
                appointments.append(entry)
            elif isinstance(entry, dict):
                # Validate required fields
                required_fields = ["start_tick", "end_tick", "location", "label"]
                if all(field in entry for field in required_fields):
                    try:
                        appt = Appointment(
                            start_tick=int(entry["start_tick"]),
                            end_tick=int(entry["end_tick"]),
                            location=str(entry["location"]),
                            label=str(entry["label"])
                        )
                        appointments.append(appt)
                    except (ValueError, TypeError) as e:
                        if self.sim_logger:
                            self.sim_logger.warning(
                            f"Invalid schedule entry {i} for persona {persona_name}: {e}"
                        )
                else:
                    missing = [f for f in required_fields if f not in entry]
                    if self.sim_logger:
                        self.sim_logger.warning(
                        f"Schedule entry {i} for persona {persona_name} missing fields: {missing}"
                    )
            else:
                if self.sim_logger:
                    self.sim_logger.warning(
                    f"Invalid schedule entry {i} for persona {persona_name}: expected dict or Appointment"
                )
        
        return appointments

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

    def load_agents(self, world_name: str, world: Optional[Any] = None) -> List["Agent"]:
        """
        Load fully initialized Agent instances from the personas.yaml file.
        
        Completes:
        - Schedule parsing and application (as Appointment objects)
        - Position initialization with validation
        - Linking agents to the world if provided
        
        Args:
            world_name (str): Name of the world.
            world (Optional[World]): World instance to link agents to.
        
        Returns:
            List[Agent]: List of fully initialized Agent instances.
        """
        # Lazy import to avoid circular dependencies
        from sim.agents.agents import Agent, Persona
        
        personas_path = os.path.join(self.get_world_path(world_name), "personas.yaml")
        with open(personas_path, 'r') as file:
            personas_data = yaml.safe_load(file).get("people", [])

        agents = []
        for persona_data in personas_data:
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
            
            # Get position - support both 'position' and 'start_place'
            initial_place = persona_data.get("position") or persona_data.get("start_place", "unknown")
            
            # Get parsed schedule (already Appointment objects from load_personas)
            calendar = persona_data.get("schedule", [])
            
            # Create Agent with fully initialized data
            agent = Agent(
                persona=persona,
                place=initial_place,
                calendar=calendar
            )
            
            # Validate and link to world if provided
            if world is not None:
                # Validate agent's position against world places
                if hasattr(world, 'places') and agent.place in world.places:
                    place_obj = world.places[agent.place]
                    initial_area = place_obj.attributes.get('initial_area') if hasattr(place_obj, 'attributes') else None
                    if initial_area and hasattr(place_obj, 'areas') and initial_area in place_obj.areas:
                        place_obj.areas[initial_area].add_agent(agent.persona.name)
                elif hasattr(world, 'places') and agent.place not in world.places:
                    if world.places:
                        default_place = next(iter(world.places))
                        if self.sim_logger:
                            self.sim_logger.warning(
                                f"Agent {agent.persona.name} position '{agent.place}' not found. Placing in default place '{default_place}'."
                            )
                        agent.place = default_place
                        place_obj = world.places[default_place]
                        initial_area = place_obj.attributes.get('initial_area') if hasattr(place_obj, 'attributes') else None
                        if initial_area and hasattr(place_obj, 'areas') and initial_area in place_obj.areas:
                            place_obj.areas[initial_area].add_agent(agent.persona.name)
            
            agents.append(agent)
            if self.sim_logger:
                self.sim_logger.debug(
                f"Loaded agent {agent.persona.name} at {agent.place} "
                f"with {len(calendar)} scheduled appointments"
            )
        
        return agents

    def validate_config(self, world_name: str, filename: str, schema: Optional[Dict[str, Any]] = None):
        """
        Validate a configuration file against a schema.
        Args:
            world_name (str): Name of the world.
            filename (str): Configuration filename to validate.
            schema (Optional[Dict[str, Any]]): Custom schema or None to use built-in.
        Returns:
            Tuple[bool, List[str]]: (is_valid, list of error messages)
        """
        data = self.load_yaml(world_name, filename)
        if data is None:
            error = f"Failed to load {filename} for validation."
            if self.sim_logger:
                self.sim_logger.error(error)
            return False, [error]

        # Use built-in validators for known config files
        result = None
        if filename == "personas.yaml":
            result = validate_personas_config(data)
        elif filename == "city.yaml":
            result = validate_city_config(data)
        elif filename == "world.yaml":
            result = validate_world_config(data)
        elif filename == "names.yaml":
            result = validate_names_config(data)
        elif schema is not None:
            from sim.utils.schema_validation import validate_nested_schema
            is_valid = validate_nested_schema(data, schema)
            return is_valid, [] if is_valid else [f"Schema validation failed for {filename}"]
        else:
            if self.sim_logger:
                self.sim_logger.warning(f"No schema available for {filename}")
            return True, []

        if hasattr(result, 'is_valid') and result.is_valid:
            if self.sim_logger:
                self.sim_logger.info(f"Validation passed for {filename} in world '{world_name}'.")
        elif hasattr(result, 'errors'):
            for error in result.errors:
                if self.sim_logger:
                    self.sim_logger.error(f"Validation error in {filename}: {error}")
        return getattr(result, 'is_valid', True), getattr(result, 'errors', [])

    def validate_all_configs(self, world_name: str) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate all configuration files for a world.
        
        Args:
            world_name (str): Name of the world.
        
        Returns:
            Tuple[bool, Dict[str, List[str]]]: (all_valid, dict of filename -> errors)
        """
        all_errors: Dict[str, List[str]] = {}
        all_valid = True
        
        configs = ["world.yaml", "city.yaml", "personas.yaml", "names.yaml"]
        for config in configs:
            is_valid, errors = self.validate_config(world_name, config)
            if not is_valid:
                all_valid = False
                all_errors[config] = errors
        
        return all_valid, all_errors

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

        is_valid, errors = self.validate_config(world_name, "places.yaml", schema)
        if not is_valid:
            if self.sim_logger:
                self.sim_logger.error(f"Failed to validate places.yaml for world '{world_name}': {errors}")
            return None

        return self.load_yaml(world_name, "places.yaml")
