from app.alchemy.db import Base
from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship

class Predict(Base):
    __tablename__ = 'predict'
    id = Column(Integer, primary_key=True)
    
    brand_id = Column(Integer, ForeignKey('brand.id'))
    stack_id = Column(Integer, ForeignKey('stack.id'))

    date = Column(Date)
    weight = Column(Float)

    brand = relationship('Brand', back_populates='predicts')
    stack = relationship('Stack', back_populates='predicts')

        
