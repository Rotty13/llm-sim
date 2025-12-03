"""
monitor.py

Provides hooks for monitoring agent behavior, resource flows, and world events during simulation runs in llm-sim.

Key Functions:
- log_agent_action: Log agent actions to console and metrics.
- log_resource_flow: Log resource movements.
- log_world_event: Log world events.
- configure_logging: Set up logging level.

LLM Usage:
- None directly; monitoring logic may be used by modules that interact with LLMs.

CLI Arguments:
- None directly; monitoring is managed by simulation scripts and world configs.
"""
import logging
from typing import Any, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from sim.utils.metrics import SimulationMetrics

logger = logging.getLogger(__name__)

# Default logging level
_log_level = logging.INFO


def configure_logging(level: int = logging.INFO):
    """
    Configure the logging level for simulation monitoring.
    
    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO, logging.WARNING)
    """
    global _log_level
    _log_level = level
    logging.basicConfig(level=level)
    logger.setLevel(level)


def log_agent_action(agent: Any, action: str, tick: int, 
                     metrics: Optional['SimulationMetrics'] = None,
                     details: Optional[Dict] = None):
    """
    Log an agent's action during simulation.
    
    Args:
        agent: The agent performing the action
        action: The action being performed
        tick: Current simulation tick
        metrics: Optional SimulationMetrics instance to record to
        details: Optional additional details about the action
    """
    # Get agent name safely
    agent_name = "Unknown"
    if hasattr(agent, 'persona') and hasattr(agent.persona, 'name'):
        agent_name = agent.persona.name
    elif hasattr(agent, 'name'):
        agent_name = agent.name
    
    # Log to console
    if logger.isEnabledFor(_log_level):
        detail_str = f" ({details})" if details else ""
        logger.log(_log_level, f"[Tick {tick}] Agent {agent_name} performed action: {action}{detail_str}")
    
    # Record to metrics if provided
    if metrics is not None:
        metrics.log_agent_action(agent_name, action, details)


def log_resource_flow(entity: str, item_id: str, qty: int, tick: int,
                      metrics: Optional['SimulationMetrics'] = None,
                      flow_type: str = "transfer"):
    """
    Log a resource flow during simulation.
    
    Args:
        entity: The entity involved (agent or place name)
        item_id: ID of the item being transferred
        qty: Quantity of the item
        tick: Current simulation tick
        metrics: Optional SimulationMetrics instance to record to
        flow_type: Type of flow ('transfer', 'consume', 'produce')
    """
    # Log to console
    if logger.isEnabledFor(_log_level):
        logger.log(_log_level, f"[Tick {tick}] {entity} resource {flow_type}: {item_id} x{qty}")
    
    # Record to metrics if provided
    if metrics is not None:
        metrics.log_resource_flow(entity, item_id, qty, flow_type)


def log_world_event(event: str, tick: int,
                    metrics: Optional['SimulationMetrics'] = None,
                    details: Optional[Dict] = None):
    """
    Log a world event during simulation.
    
    Args:
        event: Description of the world event
        tick: Current simulation tick
        metrics: Optional SimulationMetrics instance to record to
        details: Optional additional details about the event
    """
    # Log to console
    if logger.isEnabledFor(_log_level):
        detail_str = f" ({details})" if details else ""
        logger.log(_log_level, f"[Tick {tick}] World event: {event}{detail_str}")
    
    # Record to metrics if provided
    if metrics is not None:
        metrics.log_world_event(event, details)


def log_tick_start(tick: int, agent_count: int = 0, 
                   metrics: Optional['SimulationMetrics'] = None):
    """
    Log the start of a simulation tick.
    
    Args:
        tick: The tick number starting
        agent_count: Number of agents in the simulation
        metrics: Optional SimulationMetrics instance
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"[Tick {tick}] Starting with {agent_count} agents")
    
    if metrics is not None:
        metrics.set_tick(tick)


def log_tick_end(tick: int, metrics: Optional['SimulationMetrics'] = None,
                 agent_count: int = 0, active_events: int = 0):
    """
    Log the end of a simulation tick and record snapshot.
    
    Args:
        tick: The tick number ending
        metrics: Optional SimulationMetrics instance
        agent_count: Number of agents in the simulation
        active_events: Number of active events
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"[Tick {tick}] Completed")
    
    if metrics is not None:
        metrics.record_tick_snapshot(agent_count, active_events)


def log_simulation_start(metrics: Optional['SimulationMetrics'] = None):
    """
    Log the start of a simulation run.
    
    Args:
        metrics: Optional SimulationMetrics instance
    """
    logger.info("Simulation started")
    if metrics is not None:
        metrics.start()


def log_simulation_end(metrics: Optional['SimulationMetrics'] = None):
    """
    Log the end of a simulation run.
    
    Args:
        metrics: Optional SimulationMetrics instance
    """
    logger.info("Simulation ended")
    if metrics is not None:
        metrics.stop()
