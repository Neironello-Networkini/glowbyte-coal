from app.alchemy.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Date, DECIMAL
from sqlalchemy.orm import relationship
from datetime import date
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
class Supplies(Base):
    __tablename__ = 'supplies'
    
    id = Column(Integer, primary_key=True)  # Идентификатор записи
    brand_id = Column(Integer, ForeignKey('brand.id'))  # Внешний ключ на марку
    stack_id = Column(Integer, ForeignKey('stack.id'))  # Внешний ключ на штабель
    warehouse_date = Column(Date)  # Дата выгрузки на склад
    warehouse_weight = Column(DECIMAL(15, 4))  # Вес на складе
    ship_date = Column(Date)  # Дата погрузки на судно
    ship_weight = Column(DECIMAL(15, 4))  # Вес на судне
    
    brand = relationship('Brand', back_populates='supplies')
    stack = relationship('Stack', back_populates='supplies')

class SuppliesOut(BaseModel):
    id: int
    brand_id: int
    stack_id: int
    warehouse_date: date
    warehouse_weight: Optional[Decimal]
    ship_date: date
    ship_weight: Optional[Decimal]

    class Config:
        from_attributes = True