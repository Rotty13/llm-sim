from pydantic import BaseModel, Field
from typing import Optional, List, Any

class Effects(BaseModel):
    effects: Optional[List[Any]] = None
    triggers: Optional[List[Any]] = None
    side_effects: Optional[List[Any]] = None
    cooldown: Optional[Any] = None
