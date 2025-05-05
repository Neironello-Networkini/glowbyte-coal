from app.alchemy.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric, DECIMAL
from sqlalchemy.orm import relationship


class Temperature(Base):
    __tablename__ = 'temperature'
    
    id = Column(Integer, primary_key=True)  # Идентификатор записи
    brand_id = Column(Integer, ForeignKey('brand.id'))  # Внешний ключ на марку
    stack_id = Column(Integer, ForeignKey('stack.id'))  # Внешний ключ на штабель
    max_temperature = Column(DECIMAL(5, 2))  # Максимальная температура
    picket = Column(String(200))  # Пикет
    act_date = Column(Date)  # Дата акта
    shift = Column(Integer)  # Смена
    
    brand = relationship('Brand', back_populates='temperatures')
    stack = relationship('Stack', back_populates='temperatures')