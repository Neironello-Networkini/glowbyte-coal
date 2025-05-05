from pydantic import BaseModel
from datetime import date
from typing import Optional

class CreateSupplies(BaseModel):
    brand_id: int
    warehouse_id: int
    stack_number: int
    warehouse_date: date
    warehouse_weight: float
    ship_date: Optional[date] = None
    ship_weight: Optional[float] = None

class UpdateSupplies(BaseModel):
    brand_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    stack_number: Optional[int] = None
    warehouse_date: Optional[date] = None
    warehouse_weight: Optional[float] = None
    ship_date: Optional[date] = None
    ship_weight: Optional[float] = None

class DeleteSupplies(BaseModel):
    id: int 