"""
agent_loader.py

Helper for loading agents from YAML config files in llm-sim.

- Parses and validates agent data from YAML (personas.yaml)
- Returns Agent object via WorldManager
- Enforces required fields and types
- Follows project docstring and naming conventions
"""

from typing import Dict, Any


def load_agent_from_yaml(yaml_data: Dict[str, Any], world_manager) -> "Agent":
    """
    Parses and validates agent data from a YAML config (e.g., personas.yaml), returning an Agent object.

    Args:
        yaml_data (dict): Parsed YAML dictionary for a single agent.
        world_manager (WorldManager): Instance for world context and agent creation.

    Returns:
        Agent: Structured Agent object.

    Raises:
        ValueError: If required fields are missing or invalid.

    Required Fields:
        - name (str)
        - schedule (dict or list)
        - position (dict or str)

    LLM Usage:
        None (pure validation and object construction).

    CLI Arguments:
        None (intended for internal use in world loading routines).
    """
    required_fields = ["name", "schedule", "position"]
    missing = [field for field in required_fields if field not in yaml_data]
    if missing:
        raise ValueError(f"Agent config missing required fields: {missing}")

    name = yaml_data["name"]
    schedule = yaml_data["schedule"]
    position = yaml_data["position"]

    # Additional validation (type checks, etc.)
    if not isinstance(name, str) or not name:
        raise ValueError("Agent 'name' must be a non-empty string.")
    if not isinstance(schedule, (dict, list)):
        raise ValueError("Agent 'schedule' must be a dict or list.")
    if not isinstance(position, (dict, str)):
        raise ValueError("Agent 'position' must be a dict or string.")

    # Construct Agent using WorldManager's API
    agent = world_manager.create_agent(
        name=name,
        schedule=schedule,
        position=position,
        extra_fields={k: v for k, v in yaml_data.items() if k not in required_fields}
    )
    return agent
