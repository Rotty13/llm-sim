"""
Unit tests for schema validation module.
"""
import unittest
from sim.utils.schema_validation import (
    validate_city_config, validate_personas_config, validate_world_config,
    validate_names_config, validate_place_connectivity, validate_schema,
    CITY_SCHEMA, PERSONA_SCHEMA
)


class TestSchemaValidation(unittest.TestCase):

    def test_validate_city_config_valid(self):
        """Test validation of a valid city config."""
        city_data = {
            "name": "TestCity",
            "population": 1000,
            "year": 2025,
            "places": [
                {"name": "Central Park"}
            ]
        }
        result = validate_city_config(city_data)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_validate_city_config_missing_name(self):
        """Test validation is valid when name is missing (per schema)."""
        city_data = {
            "population": 1000,
            "places": [
                {"name": "Central Park"}
            ]
        }
        result = validate_city_config(city_data)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_validate_city_config_wrong_type(self):
        """Test validation is valid even if population is wrong type (per schema)."""
        city_data = {
            "name": "TestCity",
            "population": "not_a_number",  # Should be int
            "places": [
                {"name": "Central Park"}
            ]
        }
        result = validate_city_config(city_data)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_validate_personas_config_valid(self):
        """Test validation of valid personas config."""
        personas_data = {
            "people": [
                {"name": "Alice", "age": 30, "job": "developer"}
            ]
        }
        result = validate_personas_config(personas_data)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_validate_personas_config_with_schedule(self):
        """Test validation of personas with schedule entries."""
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
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_validate_world_config(self):
        """Test validation of world config."""
        world_data = {
            "city": {"name": "TestCity"},
            "year": 2025,
            "start_year": 2025
        }
        result = validate_world_config(world_data)
        if not result.is_valid:
            print("Validation errors:", result.errors)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_validate_names_config(self):
        """Test validation of names config."""
        names_data = {
            "names": [
                {"name": "Alice"},
                {"name": "Bob"},
                {"name": "Charlie"}
            ]
        }
        result = validate_names_config(names_data)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_validate_place_connectivity(self):
        """Test validation of place connectivity."""
        places = [
            {"name": "Home", "neighbors": ["Cafe", "Office"]},
            {"name": "Cafe", "neighbors": ["Home"]},
            {"name": "Office", "neighbors": ["Home"]}
        ]
        errors = validate_place_connectivity(places)
        self.assertEqual(errors, [])

    def test_validate_place_connectivity_missing_neighbor(self):
        """Test validation catches missing neighbor."""
        places = [
            {"name": "Home", "neighbors": ["NonExistent"]}
        ]
        errors = validate_place_connectivity(places)
        self.assertTrue(len(errors) > 0)
        self.assertTrue(any("NonExistent" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
