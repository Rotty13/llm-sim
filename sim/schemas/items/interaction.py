from pydantic import BaseModel, Field
from typing import Optional, List, Any

class Interaction(BaseModel):
    actions: List[str]
    affordances: Optional[List[str]] = None
    required_attributes: Optional[List[Any]] = None
    interaction_range: Optional[Any] = None
    interaction_feedback: Optional[Any] = None
