"""
schema_validation.py

Provides YAML/JSON schema validation utilities for config files in llm-sim.

This module includes:
- Functions for validating YAML/JSON data against schemas
- Pre-defined schemas for city.yaml, personas.yaml, world.yaml, and names.yaml
- Helpful error messages for validation failures

LLM Usage: None
"""
import yaml
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

def validate_yaml_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate a YAML data dict against a schema dict."""
    for key, valtype in schema.items():
        if key not in data:
            print(f"Missing key: {key}")
            return False
        if not isinstance(data[key], valtype):
            print(f"Invalid type for key: {key}. Expected {valtype}, got {type(data[key])}.")
            return False
    return True

def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate a JSON data dict against a schema dict."""
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


# ============================================================================
# Schema Definitions for Configuration Files
# ============================================================================

# Schema for world.yaml configuration
WORLD_SCHEMA = {
    "required": ["start_year"],
    "optional": ["description", "city"],
    "types": {
        "start_year": int,
        "description": str,
        "city": dict
    }
}

# Schema for city.yaml configuration
CITY_SCHEMA = {
    "required": ["places"],
    "optional": ["name", "year"],
    "types": {
        "name": str,
        "year": int,
        "places": list
    },
    "places_item": {
        "required": ["name"],
        "optional": ["category", "purpose", "description", "roles", "capabilities", "neighbors", "vendor"],
        "types": {
            "name": str,
            "category": str,
            "purpose": str,
            "description": str,
            "roles": list,
            "capabilities": list,
            "neighbors": list,
            "vendor": dict
        }
    }
}

# Schema for personas.yaml configuration
PERSONAS_SCHEMA = {
    "required": ["people"],
    "optional": [],
    "types": {
        "people": list
    },
    "people_item": {
        "required": ["name"],
        "optional": ["age", "job", "bio", "values", "goals", "start_place", "position", "schedule"],
        "types": {
            "name": str,
            "age": int,
            "job": str,
            "bio": str,
            "values": list,
            "goals": list,
            "start_place": str,
            "position": str,
            "schedule": list
        }
    },
    "schedule_item": {
        "required": ["start_tick", "end_tick", "location", "label"],
        "optional": [],
        "types": {
            "start_tick": int,
            "end_tick": int,
            "location": str,
            "label": str
        }
    }
}

# Schema for names.yaml configuration
NAMES_SCHEMA = {
    "required": [],
    "optional": ["names", "last_names"],
    "types": {
        "names": list,
        "last_names": list
    },
    "names_item": {
        "required": ["name"],
        "optional": ["sex"],
        "types": {
            "name": str,
            "sex": str
        }
    }
}


class ValidationError(Exception):
    """Exception raised for configuration validation errors."""
    pass


class ValidationResult:
    """Holds the result of a schema validation."""
    
    def __init__(self, is_valid: bool = True, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error: str):
        """Add an error message to the result."""
        self.is_valid = False
        self.errors.append(error)
    
    def __bool__(self) -> bool:
        return self.is_valid
    
    def __repr__(self) -> str:
        if self.is_valid:
            return "ValidationResult(valid=True)"
        return f"ValidationResult(valid=False, errors={self.errors})"


def validate_config(data: Dict[str, Any], schema: Dict[str, Any], 
                   config_name: str = "config") -> ValidationResult:
    """
    Validate a configuration dictionary against a schema definition.
    
    Args:
        data: The configuration data to validate.
        schema: The schema definition with 'required', 'optional', and 'types' keys.
        config_name: Name of the config file for error messages.
    
    Returns:
        ValidationResult with is_valid flag and list of errors.
    """
    result = ValidationResult()
    
    if data is None:
        result.add_error(f"{config_name}: Data is None")
        return result
    
    if not isinstance(data, dict):
        result.add_error(f"{config_name}: Expected dict, got {type(data).__name__}")
        return result
    
    # Check required fields
    for field in schema.get("required", []):
        if field not in data:
            result.add_error(f"{config_name}: Missing required field '{field}'")
    
    # Validate types for all present fields
    types = schema.get("types", {})
    for field, value in data.items():
        if field in types:
            expected_type = types[field]
            if not isinstance(value, expected_type):
                result.add_error(
                    f"{config_name}: Field '{field}' expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
    
    return result


def validate_world_config(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate a world.yaml configuration.
    
    Args:
        data: The world configuration data.
    
    Returns:
        ValidationResult with is_valid flag and list of errors.
    """
    return validate_config(data, WORLD_SCHEMA, "world.yaml")


def validate_city_config(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate a city.yaml configuration including places.
    
    Args:
        data: The city configuration data.
    
    Returns:
        ValidationResult with is_valid flag and list of errors.
    """
    result = validate_config(data, CITY_SCHEMA, "city.yaml")
    
    # Validate each place in the places list
    places = data.get("places", [])
    if isinstance(places, list):
        for i, place in enumerate(places):
            if not isinstance(place, dict):
                result.add_error(f"city.yaml: places[{i}] expected dict, got {type(place).__name__}")
                continue
            
            place_schema = CITY_SCHEMA.get("places_item", {})
            for field in place_schema.get("required", []):
                if field not in place:
                    result.add_error(f"city.yaml: places[{i}] missing required field '{field}'")
            
            place_types = place_schema.get("types", {})
            for field, value in place.items():
                if field in place_types:
                    expected_type = place_types[field]
                    if not isinstance(value, expected_type):
                        result.add_error(
                            f"city.yaml: places[{i}].{field} expected {expected_type.__name__}, "
                            f"got {type(value).__name__}"
                        )
    
    return result


def validate_personas_config(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate a personas.yaml configuration including people and their schedules.
    
    Args:
        data: The personas configuration data.
    
    Returns:
        ValidationResult with is_valid flag and list of errors.
    """
    result = validate_config(data, PERSONAS_SCHEMA, "personas.yaml")
    
    # Validate each persona in the people list
    people = data.get("people", [])
    if isinstance(people, list):
        for i, persona in enumerate(people):
            if not isinstance(persona, dict):
                result.add_error(f"personas.yaml: people[{i}] expected dict, got {type(persona).__name__}")
                continue
            
            persona_schema = PERSONAS_SCHEMA.get("people_item", {})
            for field in persona_schema.get("required", []):
                if field not in persona:
                    result.add_error(f"personas.yaml: people[{i}] missing required field '{field}'")
            
            persona_types = persona_schema.get("types", {})
            for field, value in persona.items():
                if field in persona_types:
                    expected_type = persona_types[field]
                    if not isinstance(value, expected_type):
                        result.add_error(
                            f"personas.yaml: people[{i}].{field} expected {expected_type.__name__}, "
                            f"got {type(value).__name__}"
                        )
            
            # Validate schedule entries if present
            schedule = persona.get("schedule", [])
            if isinstance(schedule, list):
                schedule_schema = PERSONAS_SCHEMA.get("schedule_item", {})
                for j, entry in enumerate(schedule):
                    if not isinstance(entry, dict):
                        result.add_error(
                            f"personas.yaml: people[{i}].schedule[{j}] expected dict, "
                            f"got {type(entry).__name__}"
                        )
                        continue
                    
                    for field in schedule_schema.get("required", []):
                        if field not in entry:
                            result.add_error(
                                f"personas.yaml: people[{i}].schedule[{j}] missing required field '{field}'"
                            )
                    
                    schedule_types = schedule_schema.get("types", {})
                    for field, value in entry.items():
                        if field in schedule_types:
                            expected_type = schedule_types[field]
                            if not isinstance(value, expected_type):
                                result.add_error(
                                    f"personas.yaml: people[{i}].schedule[{j}].{field} "
                                    f"expected {expected_type.__name__}, got {type(value).__name__}"
                                )
    
    return result


def validate_names_config(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate a names.yaml configuration.
    
    Args:
        data: The names configuration data.
    
    Returns:
        ValidationResult with is_valid flag and list of errors.
    """
    result = validate_config(data, NAMES_SCHEMA, "names.yaml")
    
    # Validate each name in the names list
    names = data.get("names", [])
    if names and isinstance(names, list):
        names_schema = NAMES_SCHEMA.get("names_item", {})
        for i, name_entry in enumerate(names):
            if not isinstance(name_entry, dict):
                result.add_error(f"names.yaml: names[{i}] expected dict, got {type(name_entry).__name__}")
                continue
            
            for field in names_schema.get("required", []):
                if field not in name_entry:
                    result.add_error(f"names.yaml: names[{i}] missing required field '{field}'")
            
            names_types = names_schema.get("types", {})
            for field, value in name_entry.items():
                if field in names_types:
                    expected_type = names_types[field]
                    if not isinstance(value, expected_type):
                        result.add_error(
                            f"names.yaml: names[{i}].{field} expected {expected_type.__name__}, "
                            f"got {type(value).__name__}"
                        )
    
    return result
