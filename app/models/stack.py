from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.alchemy.db import Base

class Stack(Base):
    __tablename__ = 'stack'
    __table_args__ = (
        # составное уникальное ограничение на (warehouse_id, name)
        UniqueConstraint('warehouse_id', 'name', name='uix_stack_warehouse_name'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouse.id'), nullable=False)

    warehouse = relationship('Warehouse', back_populates='stacks')

    supplies = relationship('Supplies', back_populates='stack', cascade="all, delete-orphan")
    temperatures = relationship('Temperature', back_populates='stack', cascade="all, delete-orphan")
    current_predicts = relationship('CurrentPredict', back_populates='stack', cascade="all, delete-orphan")
    predicts = relationship('Predict', back_populates='stack', cascade="all, delete-orphan")

    