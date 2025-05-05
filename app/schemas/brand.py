from pydantic import BaseModel

class CreateBrand(BaseModel):
    name: str

class UpdateBrand(BaseModel):
    name: str

class DeleteBrand(BaseModel):
    id: int
