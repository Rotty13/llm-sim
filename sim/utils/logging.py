"""
sim/utils/logging.py

Centralized logging utility for llm-sim simulation engine.
Tracks simulation runs, agent actions, world events, and LLM interactions.

Key Features:
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Log to file and/or console
- Structured log format: timestamp, module, event type, details
- API for logging agent actions, world events, LLM calls

Usage:
    from sim.utils.logging import sim_logger
    sim_logger.info("Agent moved", extra={"agent_id": "A1", "to": "Market"})

"""

import logging
import os
from datetime import datetime

def get_log_dir(world_name=None, session_datetime=None):
    # Use provided session_datetime for folder: YYYY-MM-DD_HHMMSS
    if session_datetime is None:
        raise ValueError("session_datetime must be provided and fixed for the entire simulation run.")
    if world_name:
        log_dir = os.path.join(os.path.dirname(__file__), f'../../outputs/{world_name}/{session_datetime}')
    else:
        log_dir = os.path.join(os.path.dirname(__file__), f'../../outputs/unknown_world/{session_datetime}')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def get_log_file(world_name=None, session_datetime=None):
    log_dir = get_log_dir(world_name, session_datetime)
    # Always use sim.log for the session
    return os.path.join(log_dir, 'sim.log')


class SimLogger:
    def __init__(self, name='llm-sim', world_name=None, session_datetime=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s %(module)s %(message)s %(extra)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh = logging.FileHandler(get_log_file(world_name, session_datetime))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def info(self, msg, extra=None):
        self.logger.info(msg, extra={'extra': extra or {}})

    def debug(self, msg, extra=None):
        self.logger.debug(msg, extra={'extra': extra or {}})

    def warning(self, msg, extra=None):
        self.logger.warning(msg, extra={'extra': extra or {}})

    def error(self, msg, extra=None):
        self.logger.error(msg, extra={'extra': extra or {}})



# Usage:
#   from sim.utils.logging import SimLogger
#   sim_logger = SimLogger(world_name="World_0").logger
#   sim_logger.info("Agent moved", extra={"agent_id": "A1", "to": "Market"})
#   sim_logger.error("LLM call failed", extra={"agent_id": "A2", "error": "Timeout"})
