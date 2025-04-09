"""
Repository for Picklist model.
"""
from typing import Dict, List, Tuple, Any, Optional
import logging
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..repository import BaseRepository
from ..models import Picklist, Warehouse
from forestfire.utils.config import WAREHOUSE_NAME

# Create logger
logger = logging.getLogger(__name__)

class PicklistRepository(BaseRepository[Picklist]):
    """Repository for handling picklist-related database operations."""
    
    def __init__(self):
        """Initialize the repository with the Picklist model."""
        super().__init__(Picklist)
    
    def fetch_picklist_data(self, read_only: bool = True) -> List[Tuple]:
        """
        Fetch all picklist data from the database.
        
        Args:
            read_only: If True, uses a read-only session
            
        Returns:
            List[Tuple]: All picklist records
        """
        def query_func(session: Session) -> List[Tuple]:
            result = session.query(Picklist).join(
                Warehouse, Picklist.warehouseid == Warehouse.id
            ).filter(
                Warehouse.name == WAREHOUSE_NAME
            ).all()
            
            # Convert ORM objects to tuples to match the original function's return type
            return [(
                p.id, 
                p.picktaskid, 
                p.warehouseid, 
                p.batchid, 
                p.x_coordinate, 
                p.y_coordinate, 
                p.sequence
            ) for p in result]
        
        try:
            return self.execute_query(query_func, read_only=read_only)
        except Exception as e:
            logger.error(f"Error fetching picklist data: {e}")
            raise
    
    def fetch_distinct_picktasks(self, read_only: bool = True) -> List[str]:
        """
        Fetch distinct picktask IDs.
        
        Args:
            read_only: If True, uses a read-only session
            
        Returns:
            List[str]: List of unique picktask IDs
        """
        def query_func(session: Session) -> List[str]:
            # Set search path
            session.execute(text("SET search_path TO nifiapp"))
            
            # Get distinct picktask IDs
            result = session.query(Picklist.picktaskid).distinct().all()
            return [row[0] for row in result]
        
        try:
            return self.execute_query(query_func, read_only=read_only)
        except Exception as e:
            logger.error(f"Error fetching distinct picktasks: {e}")
            raise
    
    def map_picklist_data(self, read_only: bool = True) -> Tuple[Dict[str, List[Tuple]], Dict[str, List[Tuple]], Dict[str, int]]:
        """
        Map picklist data by picktask ID.
        
        Args:
            read_only: If True, uses a read-only session
            
        Returns:
            Tuple containing:
                - Dict[str, List[Tuple]]: Staging locations mapping
                - Dict[str, List[Tuple]]: Task locations mapping
                - Dict[str, int]: Picktask ID to database ID mapping
        """
        try:
            rows = self.fetch_picklist_data(read_only=read_only)
            if not rows:
                logger.error("No rows returned from fetch_picklist_data")
                raise Exception("No data found in picklist table")
            
            picktasks = self.fetch_distinct_picktasks(read_only=read_only)
            if not picktasks:
                logger.error("No picktasks returned from fetch_distinct_picktasks")
                raise Exception("No distinct picktasks found")
            
            # Initialize dictionaries
            staging = {}
            taskid = {}
            id_mapping = {}
            
            # Process rows
            for row in rows:
                picktask_id = row[1]  # picktaskid is at index 1
                x_coord = row[4]  # x_coordinate is at index 4
                y_coord = row[5]  # y_coordinate is at index 5
                
                # Skip rows with missing coordinates
                if x_coord is None or y_coord is None:
                    continue
                
                # Create location tuple
                location = (x_coord, y_coord)
                
                # Add to staging dictionary
                if picktask_id not in staging:
                    staging[picktask_id] = []
                staging[picktask_id].append(location)
                
                # Add to taskid dictionary
                if picktask_id not in taskid:
                    taskid[picktask_id] = []
                taskid[picktask_id].append(location)
                
                # Add to id_mapping dictionary
                id_mapping[picktask_id] = row[0]  # id is at index 0
            
            return staging, taskid, id_mapping
        
        except Exception as e:
            logger.error(f"Error mapping picklist data: {e}")
            raise
    
    def update_batchid(self, batch_id: str, picktask_id: str, read_only: bool = False) -> None:
        """
        Update batch ID for a picktask.
        
        Args:
            batch_id: New batch ID
            picktask_id: Picktask ID to update
            read_only: If True, prevents the operation
        """
        if read_only:
            logger.warning(f"Attempted to update batch ID for picktask {picktask_id} in read-only mode")
            return
        
        def transaction_func(session: Session) -> None:
            # Set search path
            session.execute(text("SET search_path TO nifiapp"))
            
            # Update batch ID
            session.query(Picklist).filter(
                Picklist.picktaskid == picktask_id
            ).update(
                {"batchid": batch_id}
            )
        
        try:
            self.execute_transaction(transaction_func, read_only=read_only)
        except Exception as e:
            logger.error(f"Error updating batch ID: {e}")
            raise
    
    def get_optimized_data(self, read_only: bool = True) -> Tuple[List[str], List[List[Tuple]], Dict[str, List[Tuple]], List[int]]:
        """
        Get optimized picklist data for order assignment.
        
        Args:
            read_only: If True, uses a read-only session
            
        Returns:
            Tuple containing:
                - List[str]: Task IDs
                - List[List[Tuple]]: Locations list
                - Dict[str, List[Tuple]]: Staging locations
                - List[int]: Database IDs in order of task_keys
        """
        try:
            staging, taskid, id_mapping = self.map_picklist_data(read_only=read_only)
            
            # Convert to required format for optimization
            task_keys = list(taskid.keys())
            locations = [[item] for sublist in taskid.values() for item in sublist]
            picklistids = [id_mapping.get(task_id) for task_id in task_keys]
            
            return task_keys, locations, staging, picklistids
        
        except Exception as e:
            logger.error(f"Error getting optimized data: {e}")
            raise
