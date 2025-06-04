"""Repository for picklist data operations.

This module provides functionality for fetching and manipulating picklist data
from the database for warehouse order picking optimization.
"""

from typing import Dict, List, Tuple
import logging
from ..connection import DatabaseConnectionManager
from ..repository import BaseRepository
from ..exceptions import QueryError

logger = logging.getLogger(__name__)


class PicklistRepository:
    """Repository for handling picklist-related database operations"""

    def __init__(self):
        self.connection_manager = DatabaseConnectionManager()
        self.baserepository = BaseRepository()

    async def fetch_picklist_data(self, warehouse_name: str) -> List[Tuple]:
        """
        Fetch all picklist data from the database

        Returns:
            List[Tuple]: All picklist records
        """
        query = """
        SELECT p.*
        FROM nifiapp.picklist p
        JOIN synob_tabr.warehouses w ON p.warehouseid = w.id
        WHERE w.name = $1;
        """
        # asyncpg uses $1
        try:
            return await self.baserepository.execute_query(
                query, (warehouse_name,)
            )

        except Exception as e:
            logger.error("Error fetching picklist data: %s", e)
            raise QueryError("Failed to fetch picklist data") from e

    async def fetch_distinct_picktasks(self) -> List[str]:
        """
        Fetch distinct picktask IDs

        Returns:
            List[str]: List of unique picktask IDs
        """
        query = """
        SELECT DISTINCT picktaskid FROM nifiapp.picklist
        """
        try:
            distinct_pictask = await self.baserepository.execute_query(query)
            return [row[0] for row in distinct_pictask]
        except Exception as e:
            logger.error("Error fetching distinct picktasks: %s", e)
            raise QueryError("Failed to fetch distinct picktasks") from e

    async def map_picklist_data(
        self,
        warehouse_name: str,
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
            rows = await self.fetch_picklist_data(warehouse_name)
            if not rows:
                logger.error("No rows returned from fetch_picklist_data")
                raise QueryError("No data found in picklist table")
            picktasks = await self.fetch_distinct_picktasks()
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
                    (row[21], row[22]) for row in rows if row[3] == picktaskid
                ]

                # Get database ID for picktask
                db_id = next(
                    (row[0] for row in rows if row[3] == picktaskid), None
                )

                # Filter staging locations
                staging_loc = [
                    (row[67], row[68]) for row in rows if row[3] == picktaskid
                ]

                task_result[picktaskid] = filtered_values
                stage_result[picktaskid] = staging_loc
                if db_id:
                    id_mapping[picktaskid] = db_id

            return stage_result, task_result, id_mapping

        except Exception as e:
            logger.error("Error mapping picklist data: %s", e)
            raise QueryError("Failed to map picklist data") from e

    async def get_optimized_data(
        self,
        warehouse_name: str,
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
            staging, taskid, id_mapping = await self.map_picklist_data(
                warehouse_name
            )

            # Convert to required format for optimization
            task_keys = list(taskid.keys())
            locations = [
                [item] for sublist in taskid.values() for item in sublist
            ]
            picklistids = [id_mapping.get(task_id) for task_id in task_keys]

            return task_keys, locations, staging, picklistids

        except Exception as e:
            logger.error("Error getting optimized data: %s", e)
            raise QueryError("Failed to get optimized data") from e
