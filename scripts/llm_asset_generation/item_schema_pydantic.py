"""
item_schema_pydantic.py

Pydantic model for the item schema, for use with Ollama structured outputs and validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PhysicalProperties(BaseModel):
    location: str
    size: Optional[Dict[str, float]] = None
    weight: Optional[float] = None
    material: Optional[str] = None
    orientation: Optional[Dict[str, float]] = None
    stackable: bool
    quantity: Optional[int] = None
    durability: Optional[Any] = None  # int or enum

class Interaction(BaseModel):
    actions: List[str]
    affordances: Optional[List[str]] = None
    required_attributes: Optional[List[Any]] = None
    interaction_range: Optional[Any] = None
    interaction_feedback: Optional[Any] = None

class Effects(BaseModel):
    effects: Optional[List[Any]] = None
    triggers: Optional[List[Any]] = None
    side_effects: Optional[List[Any]] = None
    cooldown: Optional[Any] = None

class Lifecycle(BaseModel):
    creation: Optional[Any] = None
    destruction: Optional[Any] = None
    decay: Optional[Any] = None

class BehaviorDynamics(BaseModel):
    interaction: Interaction
    effects: Optional[Effects] = None
    lifecycle: Optional[Lifecycle] = None

class StateOwnership(BaseModel):
    state: Dict[str, Any]
    owner: Optional[str] = None
    accessibility: Optional[Any] = None

class Item(BaseModel):
    id: str
    name: str
    description: str
    type: str
    tags: Optional[List[str]] = None
    physical_properties: PhysicalProperties
    behavior_dynamics: BehaviorDynamics
    state_ownership: StateOwnership
