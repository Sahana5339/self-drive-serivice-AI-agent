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

class Booking(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})

    booking_id: Optional[int] = None
    customer_id: int
    car_id: int
    start_date: str
    end_date: str
    total_price: float




