"""
schema_validation.py

Provides YAML/JSON schema validation utilities for config files in llm-sim.
"""
import yaml
import json
from typing import Any, Dict

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
