"""
test_world_events.py

Unit tests for WorldEventDispatcher integration in World class.
Tests event routing to weather, scheduler, and agent systems.
"""
import pytest
from collections import deque
from sim.world.world import World, Place
from sim.world.event_dispatcher import WorldEventDispatcher
from sim.world.weather import WeatherManager

from sim.agents.agents import Agent
from sim.agents.persona import Persona
from sim.agents.physio import Physio
from sim.agents.modules.agent_mood import AgentMood

def make_test_agent():
    persona = Persona(name='TestAgent', age=30, job='tester', city='TestCity', bio='', values=[], goals=[])
    agent = Agent(persona=persona, place='TestPlace', physio=Physio(), mood=AgentMood())
    return agent


import collections
from sim.utils.metrics import SimulationMetrics
from sim.world.weather import WeatherManager
from sim.world.event_dispatcher import WorldEventDispatcher

def setup_world_and_agent():
    place = Place(name='TestPlace', neighbors=[], capabilities={'store'})
    agent = make_test_agent()
    place.agents = [agent]
    world = World(places={'TestPlace': place})
    world.events = collections.deque()
    world._agents = [agent]
    world.agent_locations = {}
    world.item_ownership = {}
    world.metrics = SimulationMetrics()
    world.weather_manager = WeatherManager()
    world.event_dispatcher = WorldEventDispatcher()
    world.register_event_handlers()
    return world, place, agent

def test_weather_event():
    world, _, _ = setup_world_and_agent()
    event = {'type': 'weather', 'event': 'rainy'}
    world.event_dispatcher.dispatch_event(event)
    assert world.weather_manager.current_state == 'rainy'

def test_festival_event():
    world, _, agent = setup_world_and_agent()
    event = {'type': 'festival', 'name': 'Spring Festival', 'tick': 100}
    world.event_dispatcher.dispatch_event(event)
    assert agent.mood is not None, "Agent mood is None after event dispatch!"
    assert agent.mood.get_mood('festival') == 0.2

def test_store_close_event():
    world, place, _ = setup_world_and_agent()
    event = {'type': 'store_close', 'place': 'TestPlace', 'tick': 50}
    world.event_dispatcher.dispatch_event(event)
    assert 'store' not in place.capabilities

def test_accident_event():
    world, _, agent = setup_world_and_agent()
    event = {'type': 'accident', 'place': 'TestPlace', 'tick': 10}
    world.event_dispatcher.dispatch_event(event)
    assert agent.physio is not None, "Agent physio is None after event dispatch!"
    assert agent.physio.stress == 0.5  # Physio default is 0.2, +0.3 = 0.5
