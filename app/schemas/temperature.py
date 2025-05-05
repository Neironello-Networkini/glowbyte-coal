from pydantic import BaseModel
from datetime import date
from typing import Optional

class CreateTemperature(BaseModel):
    brand_id: int
    warehouse_id: int
    stack_number: int
    max_temperature: float
    picket: str
    act_date: date
    shift: int

class UpdateTemperature(BaseModel):
    brand_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    stack_number: Optional[int] = None
    max_temperature: Optional[float] = None
    picket: Optional[str] = None
    act_date: Optional[date] = None
    shift: Optional[int] = None

class DeleteTemperature(BaseModel):
    id: int 