"""
schema_validation.py

Provides YAML/JSON schema validation utilities for config files in llm-sim.
"""
import yaml
import json
from typing import Any, Dict

def validate_yaml_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate a YAML data dict against a schema dict."""
    # Simple key/type check
    for key, valtype in schema.items():
        if key not in data or not isinstance(data[key], valtype):
            return False
    return True

def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate a JSON data dict against a schema dict."""
    for key, valtype in schema.items():
        if key not in data or not isinstance(data[key], valtype):
            return False
    return True
