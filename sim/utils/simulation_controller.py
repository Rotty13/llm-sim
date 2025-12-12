"""
simulation_controller.py - Core simulation control logic for llm-sim

Encapsulates simulation state, tick loop, and control methods. Designed to be independent of GUI/CLI.

LLM Usage: None
CLI Args: None
"""

import threading
import time

class SimulationController:
    def __init__(self, world_manager, world_name, tick_interval=0.5):
        self.world_manager = world_manager
        self.world_name = world_name
        self.tick_interval = tick_interval  # seconds per tick
        self.running = False
        self.paused = False
        self._thread = None
        self._lock = threading.Lock()
        self.current_tick = 0
        self.max_ticks = None
        self.world = None
        self.agents = []

    def start(self, max_ticks=None):
        with self._lock:
            if self.running:
                return
            self.running = True
            self.paused = False
            self.max_ticks = max_ticks
            self.current_tick = 0
            self.world = self.world_manager.load_world(self.world_name)
            self.agents = self.world_manager.load_agents_with_schedules(self.world_name)
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def _run_loop(self):
        while self.running and (self.max_ticks is None or self.current_tick < self.max_ticks):
            with self._lock:
                if self.paused:
                    continue
                # TODO: Advance simulation by one tick (call scheduler, update agents, etc.)
                self.current_tick += 1
            time.sleep(self.tick_interval)

    def pause(self):
        with self._lock:
            self.paused = True

    def resume(self):
        with self._lock:
            self.paused = False

    def stop(self):
        with self._lock:
            self.running = False
        if self._thread:
            self._thread.join()
            self._thread = None

    def step(self):
        with self._lock:
            if not self.running or self.paused:
                # TODO: Advance simulation by one tick
                self.current_tick += 1

    def set_speed(self, tick_interval):
        with self._lock:
            self.tick_interval = tick_interval

    def get_state(self):
        with self._lock:
            return {
                'tick': self.current_tick,
                'world': self.world,
                'agents': self.agents,
                'running': self.running,
                'paused': self.paused
            }
