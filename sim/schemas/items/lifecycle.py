from pydantic import BaseModel, Field
from typing import Optional, Any

class Lifecycle(BaseModel):
    creation: Optional[Any] = None
    destruction: Optional[Any] = None
    decay: Optional[Any] = None
