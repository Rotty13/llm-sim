"""
scheduler.py

Defines agent scheduling and time-based movement logic for llm-sim simulation.
Provides Appointment dataclass and enforce_schedule for managing agent schedules and simulation ticks.

Key Functions:
- run_agent_loop: Main loop for agent actions over simulation ticks.
- enforce_schedule: Enforce agent schedules and movement.

Key Classes:
- Appointment: Represents scheduled events for agents.

LLM Usage:
- None directly; scheduling logic may be used by agent/world modules that interact with LLMs.

CLI Arguments:
- None directly; scheduling is managed by simulation scripts and world configs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from sim.utils.utils import TICK_MINUTES
from sim.world import world

@dataclass
class Appointment:
    start_tick: int  # Start time of the appointment in ticks
    end_tick: int    # End time of the appointment in ticks
    location: str    # Location of the appointment
    label: str       # Label or description of the appointment

def enforce_schedule(calendar: List[Appointment], place: str, tick: int, busy_until: int) -> Optional[str]:
    """
    Return a forced MOVE() if an appointment is starting soon and agent is elsewhere.
    Skip enforcement if the agent is busy.

    Args:
        calendar (List[Appointment]): List of appointments.
        place (str): Current location of the agent.
        tick (int): Current simulation tick.
        busy_until (int): Tick until which the agent is busy.

    Returns:
        Optional[str]: MOVE() command if enforcement is needed, otherwise None.
    """
    minutes = (tick * TICK_MINUTES)

    # Skip enforcement if the agent is busy
    if tick < busy_until:
        return None

    for appt in calendar:
        if 0 <= appt.end_tick - minutes <= 15:
            if place != appt.location:
                return f'MOVE({{"to":"{appt.location}"}})'
    return None

def run_agent_loop(world: world.World, ticks: int = 100, metrics=None, sim_logger=None):
    """
    Run the main agent loop for the simulation.
    Iterates over all agents for a given number of ticks, invoking their decision/action methods.
    Args:
        world: The simulation world object containing agents and places.
        ticks: Number of simulation ticks to run.
        metrics: The SimulationMetrics object to record metrics (explicitly passed)
    """
    from sim.actions.actions import parse_action
    # Removed repetitive agent loop started log; see world_manager for agent activation logs
    # This function now processes a single tick; tick value must be provided by the caller
    tick = getattr(world, 'current_tick', None)
    if tick is None:
        raise ValueError("Current tick must be provided via world.current_tick for centralized time management.")
    if metrics is not None:
        metrics.set_tick(tick)
        metrics.record_tick_snapshot(agent_count=len(getattr(world, '_agents', [])))
    for agent in getattr(world, '_agents', []):
        if not getattr(agent, 'alive', True):
            continue
        # Enforce schedule if needed
        forced_action = enforce_schedule(getattr(agent, 'calendar', []), agent.place, tick, getattr(agent, 'busy_until', -1))
        if forced_action:
            # Normalize forced_action DSL string to dict
            action_dict = parse_action(forced_action)
            agent.perform_action(action_dict, world, tick, sim_logger=sim_logger)
        else:
            decision = agent.decide(world, agent.place, tick, None)
            agent.perform_action(decision, world, tick, sim_logger=sim_logger)
    # Optionally: log tick summary, update world state, etc.
