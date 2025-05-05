from app.alchemy.db import Base
from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import relationship

class Location(Base):
    __tablename__ = 'location'
    
    id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    
    