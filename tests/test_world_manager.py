"""
Unit tests for the WorldManager class.
"""
import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
from sim.world.world_manager import WorldManager

class TestWorldManager(unittest.TestCase):

    def setUp(self):
        self.world_manager = WorldManager(worlds_dir="test_worlds")
        os.makedirs("test_worlds", exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree("test_worlds", ignore_errors=True)

    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_create_world(self, mock_open, mock_exists, mock_makedirs):
        self.world_manager.create_world("TestWorld", city="TestCity", year=2025)
        mock_makedirs.assert_called()
        mock_open.assert_called()

    @patch("os.path.exists", return_value=True)
    @patch("shutil.rmtree")
    def test_delete_world(self, mock_rmtree, mock_exists):
        self.world_manager.delete_world("TestWorld")
        mock_rmtree.assert_called_with(os.path.join("test_worlds", "TestWorld"))

    @patch("os.listdir", return_value=["World1", "World2"])
    @patch("os.path.isdir", return_value=True)
    def test_list_worlds(self, mock_isdir, mock_listdir):
        worlds = self.world_manager.list_worlds()
        self.assertEqual(worlds, ["World1", "World2"])
        mock_listdir.assert_called_with("test_worlds")
        mock_isdir.assert_called()

    @patch("sim.world.world_manager.WorldManager.load_yaml", return_value={"name": "TestCity"})
    def test_load_city(self, mock_load_yaml):
        city = self.world_manager.load_city("TestWorld")
        self.assertEqual(city, {"name": "TestCity"})

    @patch("sim.world.world_manager.WorldManager.load_yaml", return_value={"people": [{"name": "John", "position": "home", "schedule": []}]})
    def test_load_personas(self, mock_load_yaml):
        personas = self.world_manager.load_personas("TestWorld")
        self.assertEqual(len(personas), 1)
        self.assertEqual(personas[0]["name"], "John")

if __name__ == "__main__":
    unittest.main()