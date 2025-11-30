"""
schema_validation.py

Provides YAML/JSON schema validation utilities for config files in llm-sim.
Defines schemas for city.yaml, personas.yaml, world.yaml, and names.yaml.
"""
import yaml
import json
from typing import Any, Dict, List, Optional, Union

# Schema definitions for config files
CITY_SCHEMA = {
    "required": ["name"],
    "optional": {
        "population": int,
        "year": int,
        "features": list,
        "places": list,
    },
    "types": {
        "name": str,
        "population": int,
        "year": int,
        "features": list,
        "places": list,
    }
}

PLACE_SCHEMA = {
    "required": ["name"],
    "optional": {
        "neighbors": list,
        "capabilities": list,
        "purpose": str,
        "vendor": dict,
    },
    "types": {
        "name": str,
        "neighbors": list,
        "capabilities": list,
        "purpose": str,
        "vendor": dict,
    }
}

PERSONA_SCHEMA = {
    "required": ["name"],
    "optional": {
        "age": int,
        "job": str,
        "city": str,
        "bio": str,
        "values": list,
        "goals": list,
        "position": str,
        "schedule": list,
        "role": str,
        "traits": list,
    },
    "types": {
        "name": str,
        "age": int,
        "job": str,
        "city": str,
        "bio": str,
        "values": list,
        "goals": list,
        "position": str,
        "schedule": list,
        "role": str,
        "traits": list,
    }
}

SCHEDULE_ENTRY_SCHEMA = {
    "required": ["start_tick", "end_tick", "location", "label"],
    "optional": {},
    "types": {
        "start_tick": int,
        "end_tick": int,
        "location": str,
        "label": str,
    }
}

WORLD_SCHEMA = {
    "required": [],
    "optional": {
        "city": (str, dict),
        "year": int,
        "scenario": str,
        "description": str,
    },
    "types": {
        "city": (str, dict),
        "year": int,
        "scenario": str,
        "description": str,
    }
}

PERSONAS_FILE_SCHEMA = {
    "required": [],
    "optional": {
        "people": list,
        "personas": list,
    },
    "types": {
        "people": list,
        "personas": list,
    }
}

NAMES_SCHEMA = {
    "required": [],
    "optional": {
        "names": list,
    },
    "types": {
        "names": list,
    }
}


class ValidationError(Exception):
    """Exception raised when validation fails."""
    pass


def validate_type(value: Any, expected_type: Union[type, tuple]) -> bool:
    """Check if a value matches the expected type(s)."""
    if isinstance(expected_type, tuple):
        return isinstance(value, expected_type)
    return isinstance(value, expected_type)


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any], context: str = "") -> List[str]:
    """
    Validate data against a schema.
    
    Args:
        data: The data dictionary to validate.
        schema: The schema definition with 'required', 'optional', and 'types'.
        context: Context string for error messages.
    
    Returns:
        List of validation error messages (empty if valid).
    """
    errors = []
    
    if not isinstance(data, dict):
        errors.append(f"{context}: Expected a dictionary, got {type(data).__name__}")
        return errors
    
    # Check required fields
    for key in schema.get("required", []):
        if key not in data:
            errors.append(f"{context}: Missing required key '{key}'")
    
    # Check types for all present keys
    types_def = schema.get("types", {})
    for key, value in data.items():
        if key in types_def:
            expected = types_def[key]
            if not validate_type(value, expected):
                if isinstance(expected, tuple):
                    type_names = " or ".join(t.__name__ for t in expected)
                else:
                    type_names = expected.__name__
                errors.append(f"{context}: Invalid type for '{key}'. Expected {type_names}, got {type(value).__name__}")
    
    return errors


def validate_city_config(data: Dict[str, Any]) -> List[str]:
    """Validate city.yaml configuration."""
    errors = validate_schema(data, CITY_SCHEMA, "city.yaml")
    
    # Validate places if present
    if "places" in data and isinstance(data["places"], list):
        for i, place in enumerate(data["places"]):
            place_errors = validate_schema(place, PLACE_SCHEMA, f"city.yaml places[{i}]")
            errors.extend(place_errors)
    
    return errors


def validate_personas_config(data: Dict[str, Any]) -> List[str]:
    """Validate personas.yaml configuration."""
    errors = validate_schema(data, PERSONAS_FILE_SCHEMA, "personas.yaml")
    
    # Validate personas in 'people' or 'personas' key
    personas_key = "people" if "people" in data else "personas" if "personas" in data else None
    if personas_key and isinstance(data[personas_key], list):
        for i, persona in enumerate(data[personas_key]):
            persona_errors = validate_schema(persona, PERSONA_SCHEMA, f"personas.yaml {personas_key}[{i}]")
            errors.extend(persona_errors)
            
            # Validate schedule entries if present
            if "schedule" in persona and isinstance(persona["schedule"], list):
                for j, entry in enumerate(persona["schedule"]):
                    entry_errors = validate_schema(entry, SCHEDULE_ENTRY_SCHEMA, f"personas.yaml {personas_key}[{i}] schedule[{j}]")
                    errors.extend(entry_errors)
    
    return errors


def validate_world_config(data: Dict[str, Any]) -> List[str]:
    """Validate world.yaml configuration."""
    return validate_schema(data, WORLD_SCHEMA, "world.yaml")


def validate_names_config(data: Dict[str, Any]) -> List[str]:
    """Validate names.yaml configuration."""
    return validate_schema(data, NAMES_SCHEMA, "names.yaml")


def validate_place_connectivity(places: List[Dict[str, Any]]) -> List[str]:
    """
    Validate that place neighbor relationships are consistent.
    
    Args:
        places: List of place configurations.
    
    Returns:
        List of validation error messages.
    """
    errors = []
    place_names = {p.get("name") for p in places if isinstance(p, dict)}
    
    for place in places:
        if not isinstance(place, dict):
            continue
        name = place.get("name", "unknown")
        neighbors = place.get("neighbors", [])
        
        for neighbor in neighbors:
            if neighbor not in place_names:
                errors.append(f"Place '{name}' has neighbor '{neighbor}' which does not exist")
    
    return errors


def validate_yaml_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Legacy validation function for backwards compatibility.
    Validate a YAML data dict against a schema dict.
    """
    for key, valtype in schema.items():
        if key not in data:
            print(f"Missing key: {key}")
            return False
        if not isinstance(data[key], valtype):
            print(f"Invalid type for key: {key}. Expected {valtype}, got {type(data[key])}.")
            return False
    return True


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Legacy validation function for backwards compatibility.
    Validate a JSON data dict against a schema dict.
    """
    for key, valtype in schema.items():
        if key not in data:
            print(f"Missing key: {key}")
            return False
        if not isinstance(data[key], valtype):
            print(f"Invalid type for key: {key}. Expected {valtype}, got {type(data[key])}.")
            return False
    return True

def validate_nested_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate a nested data dict against a nested schema dict."""
    for key, valtype in schema.items():
        if key not in data:
            print(f"Missing key: {key}")
            return False

        # Handle nested objects
        if isinstance(valtype, dict):
            if not isinstance(data[key], dict):
                print(f"Invalid type for key: {key}. Expected dict, got {type(data[key])}.")
                return False
            if not validate_nested_schema(data[key], valtype):
                return False

        # Handle lists with item validation
        elif isinstance(valtype, list):
            if not isinstance(data[key], list):
                print(f"Invalid type for key: {key}. Expected list, got {type(data[key])}.")
                return False
            item_schema = valtype[0] if valtype else None
            if item_schema:
                for item in data[key]:
                    if not validate_nested_schema(item, item_schema):
                        return False

        # Handle primitive types
        elif not isinstance(data[key], valtype):
            print(f"Invalid type for key: {key}. Expected {valtype}, got {type(data[key])}.")
            return False

    return True
