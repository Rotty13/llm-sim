"""
Pytest-based tests for the WorldManager class.
"""
import os
import pytest
from unittest.mock import patch, mock_open, MagicMock
from sim.world.world_manager import WorldManager

@pytest.fixture
def world_manager():
    wm = WorldManager(worlds_dir="test_worlds")
    os.makedirs("test_worlds", exist_ok=True)
    yield wm
    import shutil
    shutil.rmtree("test_worlds", ignore_errors=True)

@patch("os.makedirs")
@patch("os.path.exists", return_value=False)
@patch("builtins.open", new_callable=mock_open)
def test_create_world(mock_open, mock_exists, mock_makedirs, world_manager):
    world_manager.create_world("TestWorld", city="TestCity", year=2025)
    mock_makedirs.assert_called()
    mock_open.assert_called()

@patch("os.path.exists", return_value=True)
@patch("shutil.rmtree")
def test_delete_world(mock_rmtree, mock_exists, world_manager):
    world_manager.delete_world("TestWorld")
    mock_rmtree.assert_called_with(os.path.join("test_worlds", "TestWorld"))

@patch("os.listdir", return_value=["World1", "World2"])
@patch("os.path.isdir", return_value=True)
def test_list_worlds(mock_isdir, mock_listdir, world_manager):
    worlds = world_manager.list_worlds()
    assert worlds == ["World1", "World2"]
    mock_listdir.assert_called_with("test_worlds")
    mock_isdir.assert_called()

@patch("sim.world.world_manager.WorldManager.load_yaml", return_value={"name": "TestCity"})
def test_load_city(mock_load_yaml, world_manager):
    city = world_manager.load_city("TestWorld")
    assert city == {"name": "TestCity"}

@patch("sim.world.world_manager.WorldManager.load_yaml", return_value={"people": [{"name": "John", "position": "home", "schedule": []}]})
def test_load_personas(mock_load_yaml, world_manager):
    personas = world_manager.load_personas("TestWorld")
    assert personas is not None, "Personas should not be None"
    assert len(personas) == 1
    assert personas[0]["name"] == "John"