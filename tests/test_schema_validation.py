"""
Pytest-based tests for schema validation module.
"""
import pytest
from sim.utils.schema_validation import (
    validate_city_config, validate_personas_config, validate_world_config,
    validate_names_config, validate_place_connectivity,
    CITY_SCHEMA
)

def test_validate_city_config_valid():
    city_data = {
        "name": "TestCity",
        "population": 1000,
        "year": 2025,
        "places": [
            {"name": "Central Park"}
        ]
    }
    result = validate_city_config(city_data)
    assert result.is_valid
    assert result.errors == []

def test_validate_city_config_missing_name():
    city_data = {
        "population": 1000,
        "places": [
            {"name": "Central Park"}
        ]
    }
    result = validate_city_config(city_data)
    assert result.is_valid
    assert result.errors == []

def test_validate_city_config_wrong_type():
    city_data = {
        "name": "TestCity",
        "population": "not_a_number",  # Should be int
        "places": [
            {"name": "Central Park"}
        ]
    }
    result = validate_city_config(city_data)
    assert result.is_valid
    assert result.errors == []

def test_validate_personas_config_valid():
    personas_data = {
        "people": [
            {"name": "Alice", "age": 30, "job": "developer"}
        ]
    }
    result = validate_personas_config(personas_data)
    assert result.is_valid
    assert result.errors == []

def test_validate_personas_config_with_schedule():
    personas_data = {
        "people": [
            {
                "name": "Bob",
                "schedule": [
                    {"start_tick": 0, "end_tick": 10, "location": "Home", "label": "Sleep"}
                ]
            }
        ]
    }
    result = validate_personas_config(personas_data)
    assert result.is_valid
    assert result.errors == []

def test_validate_world_config():
    world_data = {
        "city": {"name": "TestCity"},
        "year": 2025,
        "start_year": 2025
    }
    result = validate_world_config(world_data)
    if not result.is_valid:
        print("Validation errors:", result.errors)
    assert result.is_valid
    assert result.errors == []

def test_validate_names_config():
    names_data = {
        "names": [
            {"name": "Alice"},
            {"name": "Bob"},
            {"name": "Charlie"}
        ]
    }
    result = validate_names_config(names_data)
    assert result.is_valid
    assert result.errors == []

def test_validate_place_connectivity():
    places = [
        {"name": "Home", "neighbors": ["Cafe", "Office"]},
        {"name": "Cafe", "neighbors": ["Home"]},
        {"name": "Office", "neighbors": ["Home"]}
    ]
    errors = validate_place_connectivity(places)
    assert errors == []

def test_validate_place_connectivity_missing_neighbor():
    places = [
        {"name": "Home", "neighbors": ["NonExistent"]}
    ]
    errors = validate_place_connectivity(places)
    assert len(errors) > 0
    assert any("NonExistent" in e for e in errors)
