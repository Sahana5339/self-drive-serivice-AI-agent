from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class Car(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})

    id: Optional[int] = None
    company: str
    model: str
    kms: int
    year: int
    color: str
    available: bool




