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

LOG_DIR = os.path.join(os.path.dirname(__file__), '../../outputs/llm_logs')
LOG_FILE = os.path.join(LOG_DIR, f'sim_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

os.makedirs(LOG_DIR, exist_ok=True)

class SimLogger:
    def __init__(self, name='llm-sim'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s %(module)s %(message)s %(extra)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh = logging.FileHandler(LOG_FILE)
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

# Singleton logger instance
sim_logger = SimLogger().logger

# Example API for logging simulation events
# sim_logger.info("Agent moved", extra={"agent_id": "A1", "to": "Market"})
# sim_logger.error("LLM call failed", extra={"agent_id": "A2", "error": "Timeout"})
