"""
agent_factory.py

Factory for creating Agent instances with configurable modules.
Supports dynamic instantiation based on config dict or YAML.

Key Functions:
- AgentFactory: Class for agent creation.
- create_agent: Static method to instantiate Agent with config.

LLM Usage:
- None directly; agents use LLM via agents.py.

CLI Arguments:
- None directly; used by simulation scripts and world modules.
"""
from sim.agents.agents import Agent, Persona
from typing import Dict, Any, Optional

class AgentFactory:
    """
    Factory for creating Agent instances with configurable modules.
    """
    @staticmethod
    def create_agent(persona: Persona, place: str, config: Optional[Dict[str, bool]] = None, **kwargs) -> Agent:
        """
        Create an Agent with the given persona, place, and config dict.
        Additional kwargs are passed to Agent constructor.
        """
        return Agent(persona=persona, place=place, config=config, **kwargs)
