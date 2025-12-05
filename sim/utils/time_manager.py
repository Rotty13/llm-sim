"""
time_manager.py

Provides a TimeManager class for unified simulation time handling in llm-sim.
Handles tick-to-time conversions, time-of-day, and day tracking.

Key Features:
- Set and advance simulation ticks
- Convert ticks to in-world hours, minutes, and days
- Get time-of-day string (morning, afternoon, evening, night)
- Configurable ticks per day and minutes per tick

LLM Usage:
- None directly; used by simulation modules for time calculations.

CLI Arguments:
- None directly; used internally by simulation engine.
"""

class TimeManager:
    def __init__(self, ticks_per_day: int = 288, minutes_per_tick: int = 5):
        self.ticks_per_day = ticks_per_day
        self.minutes_per_tick = minutes_per_tick
        self.tick = 0

    def set_tick(self, tick: int):
        self.tick = tick

    def advance(self, n: int = 1):
        self.tick += n

    @property
    def day(self) -> int:
        return self.tick // self.ticks_per_day

    @property
    def tick_of_day(self) -> int:
        return self.tick % self.ticks_per_day

    @property
    def minutes(self) -> int:
        return (self.tick_of_day * self.minutes_per_tick) % 60

    @property
    def hour(self) -> int:
        return (self.tick_of_day * self.minutes_per_tick) // 60

    def get_time_of_day(self) -> str:
        hour = self.hour
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'

    def get_time_str(self) -> str:
        return f"Day {self.day}, {self.hour:02d}:{self.minutes:02d}"
