"""
item_schema_pydantic.py

Pydantic model for the item schema, for use with Ollama structured outputs and validation.
"""

"""
item_schema_pydantic.py

Refactored: imports modular schema fragments for use in item construction, validation, and agent-centric knowledge.
"""

from sim.schemas.items import PhysicalProperties, Interaction, Effects, Lifecycle, Ownership
from sim.schemas.agent import AgentBelief

# Example: how to compose an item from fragments
# (In practice, each system or agent will use only the fragments it needs)



# Example agent-centric belief record
# (Each agent can have a dict of these, keyed by item id)
# agent.known_items[item_id] = AgentBelief(...)
