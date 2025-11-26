"""
scheduler.py

Defines Appointment and enforce_schedule for agent scheduling and time-based movement decisions in the simulation.
"""
from __future__ import annotations
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
