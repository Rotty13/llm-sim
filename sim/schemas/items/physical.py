from pydantic import BaseModel, Field
from typing import Optional, Dict

class PhysicalProperties(BaseModel):
    location: Optional[str] = None
    size: Dict[str, float]
    weight: float
    material: str


