from pydantic import BaseModel
from typing import Optional

class CreateWarehouse(BaseModel):
    name: str

class UpdateWarehouse(BaseModel):
    name: Optional[str] = None

class DeleteWarehouse(BaseModel):
    id: int 