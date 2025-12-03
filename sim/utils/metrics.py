"""
metrics.py

Simulation metrics and logging utilities for llm-sim.
Tracks agent actions, resource flows, and world events for analysis and export.

Key Classes:
- SimulationMetrics: Main metrics tracking class for simulation runs.

Key Methods:
- log_agent_action: Track agent actions.
- log_resource_flow: Track resource movements.
- log_world_event: Track world events.
- export_json: Export metrics to JSON file.
- export_csv: Export metrics to CSV file.

LLM Usage:
- None directly; metrics logic may be used by modules that interact with LLMs.

CLI Arguments:
- None directly; metrics are managed by simulation scripts and world configs.
"""

import json
import csv
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class SimulationMetrics:
    """
    Tracks simulation metrics including agent actions, resource flows, and world events.
    
    Attributes:
        agent_actions: Counter for (agent_name, action) pairs
        resource_flows: Counter for (entity, item_id) resource movements
        world_events: Counter for world events
        tick_history: List of per-tick metric snapshots
        start_time: Simulation start time
        log_level: Current logging level
    """
    
    def __init__(self, log_level: int = logging.INFO):
        """
        Initialize SimulationMetrics with optional log level.
        
        Args:
            log_level: Logging level for metric events (default: INFO)
        """
        self.agent_actions: Dict[tuple, int] = defaultdict(int)
        self.resource_flows: Dict[tuple, int] = defaultdict(int)
        self.world_events: Dict[str, int] = defaultdict(int)
        self.tick_history: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.log_level = log_level
        self._current_tick = 0

    def start(self):
        """Mark the start of a simulation run."""
        self.start_time = datetime.now()
        logger.log(self.log_level, f"Simulation metrics started at {self.start_time}")

    def stop(self):
        """Mark the end of a simulation run."""
        self.end_time = datetime.now()
        logger.log(self.log_level, f"Simulation metrics stopped at {self.end_time}")

    def set_tick(self, tick: int):
        """Set the current simulation tick for metric tracking."""
        self._current_tick = tick

    def log_agent_action(self, agent_name: str, action: str, details: Optional[Dict] = None):
        """
        Log an agent action with optional details.
        
        Args:
            agent_name: Name of the agent performing the action
            action: Action type (e.g., 'MOVE', 'EAT', 'WORK')
            details: Optional dictionary with additional action details
        """
        self.agent_actions[(agent_name, action)] += 1
        if logger.isEnabledFor(self.log_level):
            detail_str = f" - {details}" if details else ""
            logger.log(
                self.log_level, 
                f"[Tick {self._current_tick}] Agent {agent_name} performed: {action}{detail_str}"
            )

    def log_resource_flow(self, entity: str, item_id: str, qty: int, flow_type: str = "transfer"):
        """
        Log a resource flow between entities.
        
        Args:
            entity: Entity involved (agent or place name)
            item_id: ID of the item being transferred
            qty: Quantity of the item
            flow_type: Type of flow ('transfer', 'consume', 'produce')
        """
        self.resource_flows[(entity, item_id)] += qty
        if logger.isEnabledFor(self.log_level):
            logger.log(
                self.log_level,
                f"[Tick {self._current_tick}] Resource {flow_type}: {entity} -> {item_id} x{qty}"
            )

    def log_world_event(self, event: str, details: Optional[Dict] = None):
        """
        Log a world event.
        
        Args:
            event: Event type or description
            details: Optional dictionary with event details
        """
        self.world_events[event] += 1
        if logger.isEnabledFor(self.log_level):
            detail_str = f" - {details}" if details else ""
            logger.log(self.log_level, f"[Tick {self._current_tick}] World event: {event}{detail_str}")

    def record_tick_snapshot(self, agent_count: int = 0, active_events: int = 0):
        """
        Record a snapshot of metrics for the current tick.
        
        Args:
            agent_count: Number of active agents
            active_events: Number of active events
        """
        snapshot = {
            "tick": self._current_tick,
            "agent_actions": sum(v for k, v in self.agent_actions.items()),
            "resource_flows": sum(v for k, v in self.resource_flows.items()),
            "world_events": sum(v for v in self.world_events.values()),
            "agent_count": agent_count,
            "active_events": active_events
        }
        self.tick_history.append(snapshot)

    def summary(self) -> Dict[str, Any]:
        """
        Return a summary of all collected metrics.
        
        Returns:
            Dictionary containing:
            - agent_actions: Dict of (agent, action) -> count
            - resource_flows: Dict of (entity, item) -> quantity
            - world_events: Dict of event -> count
            - simulation_info: Start/end times and duration
        """
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            "agent_actions": {f"{k[0]}:{k[1]}": v for k, v in self.agent_actions.items()},
            "resource_flows": {f"{k[0]}:{k[1]}": v for k, v in self.resource_flows.items()},
            "world_events": dict(self.world_events),
            "simulation_info": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "duration_seconds": duration,
                "total_ticks": self._current_tick
            }
        }

    def export_json(self, filepath: str) -> bool:
        """
        Export metrics to a JSON file.
        
        Args:
            filepath: Path to the output JSON file
        
        Returns:
            True if export succeeded, False otherwise
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.summary(), f, indent=2)
            logger.info(f"Exported metrics to JSON: {filepath}")
            return True
        except IOError as e:
            logger.error(f"Failed to export metrics to JSON: {e}")
            return False

    def export_csv(self, filepath: str) -> bool:
        """
        Export metrics tick history to a CSV file.
        
        Args:
            filepath: Path to the output CSV file
        
        Returns:
            True if export succeeded, False otherwise
        """
        try:
            if not self.tick_history:
                logger.warning("No tick history to export")
                return False
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.tick_history[0].keys())
                writer.writeheader()
                writer.writerows(self.tick_history)
            logger.info(f"Exported metrics to CSV: {filepath}")
            return True
        except IOError as e:
            logger.error(f"Failed to export metrics to CSV: {e}")
            return False

    def reset(self):
        """Reset all metrics to initial state."""
        self.agent_actions.clear()
        self.resource_flows.clear()
        self.world_events.clear()
        self.tick_history.clear()
        self.start_time = None
        self.end_time = None
        self._current_tick = 0
