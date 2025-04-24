"""Repository for picklist data operations.

This module provides functionality for fetching and manipulating picklist data
from the database for warehouse order picking optimization.
"""

from typing import Dict, List, Tuple
import logging
from ..connection import DatabaseConnectionManager
from ..repository import BaseRepository
from ..exceptions import QueryError
from forestfire.utils.config import WAREHOUSE_NAME

logger = logging.getLogger(__name__)

class PicklistRepository:
    """Repository for handling picklist-related database operations"""

    def __init__(self):
        self.connection_manager = DatabaseConnectionManager()
        self.baserepository = BaseRepository()

    def fetch_picklist_data(self) -> List[Tuple]:
        """
        Fetch all picklist data from the database

        Returns:
            List[Tuple]: All picklist records
        """
        query = """
        SELECT p.*
        FROM nifiapp.picklist p
        JOIN synob_tabr.warehouses w ON p.warehouseid = w.id
        WHERE w.name = %s;
        """
        try:
            return self.baserepository.execute_query(query, (WAREHOUSE_NAME,))

        except Exception as e:
            logger.error("Error fetching picklist data: %s", e)
            raise QueryError("Failed to fetch picklist data: %s" % e) from e

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
            distinct_pictask = self.baserepository.execute_query(query)
            return [row[0] for row in distinct_pictask]
        except Exception as e:
            logger.error("Error fetching distinct picktasks: %s", e)
            raise QueryError(
                "Failed to fetch distinct picktasks: %s" % e
            ) from e

    def map_picklist_data(
        self
    ) -> Tuple[Dict[str, List[Tuple]], Dict[str, List[Tuple]], Dict[str, int]]:
        """
        Map picklist data by picktask ID

        Returns:
            Tuple containing:
                - Dict[str, List[Tuple]]: Staging locations mapping
                - Dict[str, List[Tuple]]: Task locations mapping
                - Dict[str, int]: Picktask ID to database ID mapping
        """
        try:
            rows = self.fetch_picklist_data()
            if not rows:
                logger.error("No rows returned from fetch_picklist_data")
                raise QueryError("No data found in picklist table")
            picktasks = self.fetch_distinct_picktasks()
            if not picktasks:
                logger.error(
                    "No picktasks returned from fetch_distinct_picktasks"
                )
                raise QueryError("No distinct picktasks found")

            task_result: Dict[str, List[Tuple]] = {}
            stage_result: Dict[str, List[Tuple]] = {}
            id_mapping: Dict[str, int] = {}  # New mapping for database IDs

            for picktaskid in picktasks:
                # Filter pick locations and get IDs
                filtered_values = [
                    (row[21], row[22])
                    for row in rows
                    if row[3] == picktaskid
                ]

                # Get database ID for picktask
                db_id = next(
                    (row[0] for row in rows if row[3] == picktaskid), None
                )

                # Filter staging locations
                staging_loc = [
                    (row[67], row[68])
                    for row in rows
                    if row[3] == picktaskid
                ]

                task_result[picktaskid] = filtered_values
                stage_result[picktaskid] = staging_loc
                if db_id:
                    id_mapping[picktaskid] = db_id

            return stage_result, task_result, id_mapping

        except Exception as e:
            logger.error("Error mapping picklist data: %s", e)
            raise QueryError("Failed to map picklist data: %s" % e) from e



    def update_batchid(self, batch_id: str, picklist_id: str) -> None:
        """
        Update batch ID for a picktask

        Args:
            batch_id (str): New batch ID
            picktask_id (str): Picktask ID to update
        """
        query = """
        SET search_path TO nifiapp;
        UPDATE picklist
        SET batchid = %s
        WHERE picktaskid = %s;
        """
        try:
            self.baserepository.execute_query(query, (batch_id, picklist_id))
        except Exception as e:
            logger.error("Error updating batch ID: %s", e)
            raise QueryError("Failed to update batch ID: %s" % e) from e


    def get_optimized_data(
        self
    ) -> Tuple[List[str], List[List[Tuple]], Dict[str, List[Tuple]], List[int]]:
        """
        Get optimized picklist data for order assignment

        Returns:
            Tuple containing:
                - List[str]: Task IDs
                - List[List[Tuple]]: Locations list
                - Dict[str, List[Tuple]]: Staging locations
                - List[int]: Database IDs in order of task_keys
        """
        try:
            staging, taskid, id_mapping = self.map_picklist_data()

            # Convert to required format for optimization
            task_keys = list(taskid.keys())
            locations = [
                [item] for sublist in taskid.values() for item in sublist
            ]
            picklistids = [id_mapping.get(task_id) for task_id in task_keys]

            return task_keys, locations, staging, picklistids

        except Exception as e:
            logger.error("Error getting optimized data: %s", e)
            raise QueryError("Failed to get optimized data: %s" % e) from e
