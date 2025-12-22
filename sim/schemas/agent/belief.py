from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class AgentBelief(BaseModel):
    id: str
    subjective_value: Optional[float] = None
    known_properties: Optional[Dict[str, Any]] = None  # e.g., {'species': 'Ficus', 'mature_size': '1.5m'}
    last_seen_with: Optional[str] = None
    suspected_owner: Optional[str] = None
    notes: Optional[str] = None
