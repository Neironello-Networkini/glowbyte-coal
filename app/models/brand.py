from app.alchemy.db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Brand(Base):
    __tablename__ = 'brand'
    
    id = Column(Integer, primary_key=True)  # Идентификатор марки
    name = Column(String(100), unique=True)  # Название марки
    
    supplies = relationship('Supplies', back_populates='brand', cascade="all, delete-orphan")
    temperatures = relationship('Temperature', back_populates='brand', cascade="all, delete-orphan")
    predicts = relationship('Predict', back_populates='brand', cascade="all, delete-orphan")
    current_predicts = relationship('CurrentPredict', back_populates='brand', cascade="all, delete-orphan")
