"""
test_time_manager.py

Unit tests for the TimeManager class in sim.utils.time_manager.
"""
import pytest
from sim.utils.time_manager import TimeManager

def test_initialization_defaults():
    tm = TimeManager()
    assert tm.ticks_per_day == 288
    assert tm.minutes_per_tick == 5
    assert tm.tick == 0

def test_set_and_advance_tick():
    tm = TimeManager()
    tm.set_tick(10)
    assert tm.tick == 10
    tm.advance(5)
    assert tm.tick == 15

def test_day_and_tick_of_day():
    tm = TimeManager(ticks_per_day=144, minutes_per_tick=10)
    tm.set_tick(145)
    assert tm.day == 1
    assert tm.tick_of_day == 1

def test_hour_and_minutes():
    tm = TimeManager(ticks_per_day=144, minutes_per_tick=10)
    tm.set_tick(6)  # 6*10 = 60 min = 1:00
    assert tm.hour == 1
    assert tm.minutes == 0
    tm.set_tick(7)  # 7*10 = 70 min = 1:10
    assert tm.hour == 1
    assert tm.minutes == 10
    tm.set_tick(143)  # Last tick of day: 143*10 = 1430 min = 23:50
    assert tm.hour == 23
    assert tm.minutes == 50

def test_time_of_day():
    tm = TimeManager(ticks_per_day=144, minutes_per_tick=10)
    # 6:00 (hour 6)
    tm.set_tick(36)
    assert tm.get_time_of_day() == 'morning'
    # 13:00 (hour 13)
    tm.set_tick(78)
    assert tm.get_time_of_day() == 'afternoon'
    # 18:00 (hour 18)
    tm.set_tick(108)
    assert tm.get_time_of_day() == 'evening'
    # 2:00 (hour 2)
    tm.set_tick(12)
    assert tm.get_time_of_day() == 'night'

def test_time_str():
    tm = TimeManager(ticks_per_day=144, minutes_per_tick=10)
    tm.set_tick(0)
    assert tm.get_time_str() == 'Day 0, 00:00'
    tm.set_tick(143)
    assert tm.get_time_str() == 'Day 0, 23:50'
    tm.set_tick(144)
    assert tm.get_time_str() == 'Day 1, 00:00'
