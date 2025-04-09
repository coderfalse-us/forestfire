"""
SQLAlchemy ORM models for database tables.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Warehouse(Base):
    """Model for warehouses table."""
    __tablename__ = 'warehouses'
    __table_args__ = {'schema': 'synob_tabr'}
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    # Relationships
    picklists = relationship("Picklist", back_populates="warehouse")
    
    def __repr__(self):
        return f"<Warehouse(id={self.id}, name='{self.name}')>"


class Picklist(Base):
    """Model for picklist table."""
    __tablename__ = 'picklist'
    __table_args__ = {'schema': 'nifiapp'}
    
    id = Column(Integer, primary_key=True)
    picktaskid = Column(String, nullable=False)
    warehouseid = Column(Integer, ForeignKey('synob_tabr.warehouses.id'))
    batchid = Column(String)
    x_coordinate = Column(Float)
    y_coordinate = Column(Float)
    sequence = Column(Integer)
    
    # Relationships
    warehouse = relationship("Warehouse", back_populates="picklists")
    
    def __repr__(self):
        return f"<Picklist(id={self.id}, picktaskid='{self.picktaskid}', batchid='{self.batchid}')>"
    
    @property
    def location(self):
        """Get the location as a tuple."""
        return (self.x_coordinate, self.y_coordinate)


class BatchPickSequence(Base):
    """Model for batch_pick_sequence table."""
    __tablename__ = 'batch_pick_sequence'
    __table_args__ = {'schema': 'nifiapp'}
    
    id = Column(Integer, primary_key=True)
    batchid = Column(String, nullable=False)
    picktaskid = Column(String, nullable=False)
    sequence = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<BatchPickSequence(id={self.id}, batchid='{self.batchid}', picktaskid='{self.picktaskid}', sequence={self.sequence})>"


# Add more models as needed for your database schema
# For example, if you have tables for pickers, orders, etc.

class Picker(Base):
    """Model for pickers table (if exists)."""
    __tablename__ = 'pickers'
    __table_args__ = {'schema': 'nifiapp'}
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    x_coordinate = Column(Float)
    y_coordinate = Column(Float)
    capacity = Column(Integer)
    
    def __repr__(self):
        return f"<Picker(id={self.id}, name='{self.name}', capacity={self.capacity})>"
    
    @property
    def location(self):
        """Get the location as a tuple."""
        return (self.x_coordinate, self.y_coordinate)
