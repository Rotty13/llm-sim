from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class Ownership(BaseModel):
    owner: Optional[str] = None
    accessibility: Optional[Any] = None
    state: Optional[Dict[str, Any]] = None
