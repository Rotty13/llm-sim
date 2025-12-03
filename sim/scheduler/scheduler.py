from __future__ import annotations

def run_agent_loop(world, ticks: int = 100):
    """
    Run the main agent loop for the simulation.
    Iterates over all agents for a given number of ticks, invoking their decision/action methods.
    Args:
        world: The simulation world object containing agents and places.
        ticks: Number of simulation ticks to run.
    """
    for tick in range(ticks):
        # Advance time in world (if needed)
        if hasattr(world, 'metrics'):
            world.metrics.set_tick(tick)
        for agent in getattr(world, '_agents', []):
            if not getattr(agent, 'alive', True):
                continue
            # Enforce schedule if needed
            forced_action = enforce_schedule(getattr(agent, 'calendar', []), agent.place, tick, getattr(agent, 'busy_until', -1))
            if forced_action:
                agent.perform_action(forced_action, world, tick)
            else:
                decision = agent.decide(world, agent.place, tick, None)
                agent.perform_action(decision["action"], world, tick)
        # Optionally: log tick summary, update world state, etc.

"""
scheduler.py

Defines Appointment and enforce_schedule for agent scheduling and time-based movement decisions in the simulation.
"""
from dataclasses import dataclass
from typing import List, Optional
from sim.utils.utils import TICK_MINUTES

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
