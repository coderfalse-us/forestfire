from typing import Dict, List, Tuple, Any
import logging
from .connection import DatabaseConnectionManager
from .exceptions import QueryError

logger = logging.getLogger(__name__)

class PicklistRepository:
    """Repository for handling picklist-related database operations"""

    def __init__(self):
        self.connection_manager = DatabaseConnectionManager()

    def fetch_picklist_data(self) -> List[Tuple]:
        """
        Fetch all picklist data from the database
        
        Returns:
            List[Tuple]: All picklist records
        """
        query = """
        SET search_path TO nifiapp;
        SELECT * FROM picklist;
        """
        try:
            with self.connection_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching picklist data: {e}")
            raise QueryError(f"Failed to fetch picklist data: {e}")

    def fetch_distinct_picktasks(self) -> List[str]:
        """
        Fetch distinct picktask IDs
        
        Returns:
            List[str]: List of unique picktask IDs
        """
        query = """
        SET search_path TO nifiapp;
        SELECT DISTINCT picktaskid FROM picklist;
        """
        try:
            with self.connection_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching distinct picktasks: {e}")
            raise QueryError(f"Failed to fetch distinct picktasks: {e}")

    def map_picklist_data(self) -> Tuple[Dict[str, List[Tuple]], Dict[str, List[Tuple]]]:
        """
        Map picklist data by picktask ID
        
        Returns:
            Tuple[Dict, Dict]: Staging and task mappings
        """
        try:
            rows = self.fetch_picklist_data()
            picktasks = self.fetch_distinct_picktasks()
            
            task_result: Dict[str, List[Tuple]] = {}
            stage_result: Dict[str, List[Tuple]] = {}

            for picktaskid in picktasks:
                # Filter pick locations
                filtered_values = [
                    (row[21], row[22])
                    for row in rows
                    if row[3] == picktaskid
                ]
                
                # Filter staging locations
                staging_loc = [
                    (row[67], row[68])
                    for row in rows
                    if row[3] == picktaskid
                ]

                task_result[picktaskid] = filtered_values
                stage_result[picktaskid] = staging_loc

            return stage_result, task_result

        except Exception as e:
            logger.error(f"Error mapping picklist data: {e}")
            raise QueryError(f"Failed to map picklist data: {e}")

    def get_optimized_data(self) -> Tuple[List[str], List[List[Tuple]], Dict[str, List[Tuple]]]:
        """
        Get optimized picklist data for order assignment
        
        Returns:
            Tuple containing:
                - List[str]: Task IDs
                - List[List[Tuple]]: Locations list
                - Dict[str, List[Tuple]]: Staging locations
        """
        try:
            staging, taskid = self.map_picklist_data()
            
            # Convert to required format for optimization
            task_keys = list(taskid.keys())
            locations = [[item] for sublist in taskid.values() for item in sublist]
            
            return task_keys, locations, staging

        except Exception as e:
            logger.error(f"Error getting optimized data: {e}")
            raise QueryError(f"Failed to get optimized data: {e}")