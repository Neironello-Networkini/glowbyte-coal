from app.alchemy.db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Warehouse(Base):
    __tablename__ = 'warehouse'
    
    id = Column(Integer, primary_key=True)  # Идентификатор склада
    name = Column(String(100))  # Название склада
    
    stacks = relationship('Stack', back_populates='warehouse', cascade="all, delete-orphan")  # uselist=True по умолчанию
