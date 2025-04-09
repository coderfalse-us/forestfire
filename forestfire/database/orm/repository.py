"""
Base repository class for ORM operations.
"""
from typing import TypeVar, Generic, Type, List, Optional, Any, Dict, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .base import get_db_session
from .models import Base
import logging

# Create logger
logger = logging.getLogger(__name__)

# Define generic type for models
T = TypeVar('T', bound=Base)

class BaseRepository(Generic[T]):
    """
    Base repository class for ORM operations.
    
    This class provides common database operations for a specific model.
    It enforces read-only operations by default.
    """
    
    def __init__(self, model_class: Type[T]):
        """
        Initialize the repository with a model class.
        
        Args:
            model_class: SQLAlchemy model class
        """
        self.model_class = model_class
    
    def get_by_id(self, id: Any, read_only: bool = True) -> Optional[T]:
        """
        Get a record by its ID.
        
        Args:
            id: Primary key value
            read_only: If True, uses a read-only session
            
        Returns:
            Model instance or None if not found
        """
        with get_db_session(read_only=read_only) as session:
            return session.query(self.model_class).get(id)
    
    def get_all(self, read_only: bool = True) -> List[T]:
        """
        Get all records.
        
        Args:
            read_only: If True, uses a read-only session
            
        Returns:
            List of model instances
        """
        with get_db_session(read_only=read_only) as session:
            return session.query(self.model_class).all()
    
    def find_by(self, criteria: Dict[str, Any], read_only: bool = True) -> List[T]:
        """
        Find records by criteria.
        
        Args:
            criteria: Dictionary of field names and values
            read_only: If True, uses a read-only session
            
        Returns:
            List of model instances
        """
        with get_db_session(read_only=read_only) as session:
            query = session.query(self.model_class)
            for key, value in criteria.items():
                query = query.filter(getattr(self.model_class, key) == value)
            return query.all()
    
    def find_one_by(self, criteria: Dict[str, Any], read_only: bool = True) -> Optional[T]:
        """
        Find one record by criteria.
        
        Args:
            criteria: Dictionary of field names and values
            read_only: If True, uses a read-only session
            
        Returns:
            Model instance or None if not found
        """
        with get_db_session(read_only=read_only) as session:
            query = session.query(self.model_class)
            for key, value in criteria.items():
                query = query.filter(getattr(self.model_class, key) == value)
            return query.first()
    
    def execute_query(self, query_func, read_only: bool = True) -> Any:
        """
        Execute a custom query function.
        
        Args:
            query_func: Function that takes a session and returns a query result
            read_only: If True, uses a read-only session
            
        Returns:
            Query result
        """
        with get_db_session(read_only=read_only) as session:
            return query_func(session)
    
    # Write operations - these should be used with caution
    # They are disabled by default (read_only=True)
    
    def create(self, data: Dict[str, Any], read_only: bool = True) -> Optional[T]:
        """
        Create a new record.
        
        Args:
            data: Dictionary of field names and values
            read_only: If True, prevents the operation
            
        Returns:
            Created model instance or None if read_only is True
        """
        if read_only:
            logger.warning("Attempted to create a record in read-only mode")
            return None
        
        with get_db_session(read_only=False) as session:
            instance = self.model_class(**data)
            session.add(instance)
            session.flush()
            return instance
    
    def update(self, id: Any, data: Dict[str, Any], read_only: bool = True) -> Optional[T]:
        """
        Update a record.
        
        Args:
            id: Primary key value
            data: Dictionary of field names and values
            read_only: If True, prevents the operation
            
        Returns:
            Updated model instance or None if read_only is True or record not found
        """
        if read_only:
            logger.warning(f"Attempted to update record {id} in read-only mode")
            return None
        
        with get_db_session(read_only=False) as session:
            instance = session.query(self.model_class).get(id)
            if instance:
                for key, value in data.items():
                    setattr(instance, key, value)
                session.flush()
                return instance
            return None
    
    def delete(self, id: Any, read_only: bool = True) -> bool:
        """
        Delete a record.
        
        Args:
            id: Primary key value
            read_only: If True, prevents the operation
            
        Returns:
            True if deleted, False otherwise
        """
        if read_only:
            logger.warning(f"Attempted to delete record {id} in read-only mode")
            return False
        
        with get_db_session(read_only=False) as session:
            instance = session.query(self.model_class).get(id)
            if instance:
                session.delete(instance)
                return True
            return False
    
    def bulk_create(self, data_list: List[Dict[str, Any]], read_only: bool = True) -> List[T]:
        """
        Create multiple records.
        
        Args:
            data_list: List of dictionaries with field names and values
            read_only: If True, prevents the operation
            
        Returns:
            List of created model instances or empty list if read_only is True
        """
        if read_only:
            logger.warning(f"Attempted to bulk create {len(data_list)} records in read-only mode")
            return []
        
        with get_db_session(read_only=False) as session:
            instances = [self.model_class(**data) for data in data_list]
            session.add_all(instances)
            session.flush()
            return instances
    
    def execute_transaction(self, transaction_func, read_only: bool = True) -> Any:
        """
        Execute a custom transaction function.
        
        Args:
            transaction_func: Function that takes a session and performs operations
            read_only: If True, prevents the operation
            
        Returns:
            Transaction result or None if read_only is True
        """
        if read_only:
            logger.warning("Attempted to execute a transaction in read-only mode")
            return None
        
        with get_db_session(read_only=False) as session:
            return transaction_func(session)
