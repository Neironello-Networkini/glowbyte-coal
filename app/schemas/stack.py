from pydantic import BaseModel

class CreateStack(BaseModel):
    name: str
    warehouse: str

class UpdateStack(BaseModel):
    name: str
    warehouse: str
