import pytest
from sim.world.place import Area
from sim.world.world import Place
from sim.inventory.inventory import Inventory


def test_place_with_areas():
    # Create areas
    room1 = Area(name="Room1", description="First room")
    room2 = Area(name="Room2", description="Second room")
    # Create place and add areas
    place = Place(name="TestBuilding", neighbors=[], capabilities=set(), purpose="building")
    place.add_area(room1)
    place.add_area(room2)
    assert "Room1" in place.areas
    assert "Room2" in place.areas
    # Add agent to Room1
    room1.add_agent("Alice")
    assert "Alice" in room1.agents_present
    # Move agent to Room2
    room1.remove_agent("Alice")
    room2.add_agent("Alice")
    assert "Alice" not in room1.agents_present
    assert "Alice" in room2.agents_present
    # Add item to Room2
    room2.add_item("apple", 3)
    assert room2.has_item("apple", 3)
    room2.remove_item("apple", 2)
    assert room2.has_item("apple", 1)


def test_initial_area_attribute():
    place = Place(name="TestBuilding", neighbors=[], capabilities=set(), purpose="building")
    room1 = Area(name="Lobby")
    place.add_area(room1)
    place.attributes["initial_area"] = "Lobby"
    assert place.attributes["initial_area"] == "Lobby"
    assert "Lobby" in place.areas
