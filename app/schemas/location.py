from pydantic import BaseModel

class CreateLocation(BaseModel):
    latitude: float
    longitude: float
