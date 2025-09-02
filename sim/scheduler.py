from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

TICK_MINUTES = 5

@dataclass
class Appointment:
    at_min: int
    place: str
    label: str

def enforce_schedule(calendar: List[Appointment], place: str, tick: int) -> Optional[str]:
    """Return a forced MOVE() if an appointment is starting soon and agent is elsewhere."""
    minutes = (tick * TICK_MINUTES)
    for appt in calendar:
        if 0 <= appt.at_min - minutes <= 15:
            if place != appt.place:
                return f'MOVE({{"to":"{appt.place}"}})'
    return None
