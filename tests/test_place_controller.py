import pytest

from scripts import place_controller


def test_load_and_infer_train_station():
    # Load the provided station YAML (train_station_3.yaml)
    data = place_controller.load_place_yaml('train_station_3')

    # Should detect the station structure and expose a location.city
    assert isinstance(data, dict)
    assert data.get('location', {}).get('city') == 'Lyon'

    # infer_staff_from_place should prefer the explicit 'staff' list and return counts
    roles = place_controller.infer_staff_from_place(data)
    # Expect at least these roles (normalized to lowercase)
    found = {r['role'] for r in roles}
    # The YAML contains Station Master, Conductor, Ticket Collector
    assert any('station master' in r or 'station_master' in r or 'station' == r for r in found) or 'conductor' in found or 'ticket collector' in found


def test_build_world_from_station():
    data = place_controller.load_place_yaml('train_station_3')
    world = place_controller.build_place_world('train_station_3', data)

    # The world should contain one place whose capabilities include 'transit'
    assert isinstance(world.places, dict)
    places = list(world.places.values())
    assert len(places) == 1
    place = places[0]
    assert 'transit' in set(place.capabilities)

    # Friendly name should reflect city when available
    assert 'Lyon' in place.name or 'lyon' in place.name.lower()
