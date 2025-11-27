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
            "year": 2025
        }
        errors = validate_city_config(city_data)
        self.assertEqual(errors, [])

    def test_validate_city_config_missing_name(self):
        """Test validation fails when name is missing."""
        city_data = {
            "population": 1000
        }
        errors = validate_city_config(city_data)
        self.assertTrue(any("name" in e for e in errors))

    def test_validate_city_config_wrong_type(self):
        """Test validation fails with wrong type."""
        city_data = {
            "name": "TestCity",
            "population": "not_a_number"  # Should be int
        }
        errors = validate_city_config(city_data)
        self.assertTrue(any("population" in e for e in errors))

    def test_validate_personas_config_valid(self):
        """Test validation of valid personas config."""
        personas_data = {
            "people": [
                {"name": "Alice", "age": 30, "job": "developer"}
            ]
        }
        errors = validate_personas_config(personas_data)
        self.assertEqual(errors, [])

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
        errors = validate_personas_config(personas_data)
        self.assertEqual(errors, [])

    def test_validate_world_config(self):
        """Test validation of world config."""
        world_data = {
            "city": "TestCity",
            "year": 2025
        }
        errors = validate_world_config(world_data)
        self.assertEqual(errors, [])

    def test_validate_names_config(self):
        """Test validation of names config."""
        names_data = {
            "names": ["Alice", "Bob", "Charlie"]
        }
        errors = validate_names_config(names_data)
        self.assertEqual(errors, [])

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
