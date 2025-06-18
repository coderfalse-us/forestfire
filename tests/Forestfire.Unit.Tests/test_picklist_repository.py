"""Tests for the PicklistRepository class.

This module contains tests for the PicklistRepository class used for
picklist-related database operations.
"""

import pytest
from unittest.mock import patch
from src.database.services.picklist import PicklistRepository
from src.database.exceptions import QueryError
from src.utils.config import TEST_WAREHOUSE_NAME as WAREHOUSE_NAME


class TestPicklistRepositoryComprehensive:
    """Comprehensive test cases for the PicklistRepository class."""

    @pytest.mark.asyncio
    @patch("src.database.repository.BaseRepository.execute_query")
    async def test_fetch_picklist_data_with_warehouse(self, mock_execute_query):
        """Test fetching picklist data with warehouse filter."""
        # Arrange
        mock_records = [
            {
                "id": 1,
                "picktask_id": "task1",
                "pick_loc_x": 10,
                "pick_loc_y": 20,
                "stage_loc_x": 30,
                "stage_loc_y": 40,
                "accountid": "account1",
                "businessunitid": "business1",
                "warehouseid": "warehouse1",
            },
            {
                "id": 2,
                "picktask_id": "task2",
                "pick_loc_x": 30,
                "pick_loc_y": 40,
                "stage_loc_x": 50,
                "stage_loc_y": 60,
                "accountid": "account2",
                "businessunitid": "business2",
                "warehouseid": "warehouse2",
            },
        ]
        mock_execute_query.return_value = mock_records
        repo = PicklistRepository()

        # Act
        result = await repo.fetch_picklist_data(WAREHOUSE_NAME)

        # Assert
        assert result == mock_execute_query.return_value
        mock_execute_query.assert_called_once_with(
            """
        SELECT
            p.id AS id,
            p.picktaskid AS picktask_id,
            p.xcoordinate AS pick_loc_x,
            p.ycoordinate AS pick_loc_y,
            p.stage_x AS stage_loc_x,
            p.stage_y AS stage_loc_y
        FROM nifiapp.picklist p
        JOIN synob_tabr.warehouses w ON p.warehouseid = w.id
        WHERE w.name = $1;
        """,
            (WAREHOUSE_NAME,),
        )

    @pytest.mark.asyncio
    @patch("src.database.repository.BaseRepository.execute_query")
    async def test_fetch_distinct_picktasks(self, mock_execute_query):
        """Test fetching distinct picktasks."""
        # Arrange
        mock_execute_query.return_value = [("task1",), ("task2",)]
        repo = PicklistRepository()

        # Act
        result = await repo.fetch_distinct_picktasks()

        # Assert
        assert result == ["task1", "task2"]
        mock_execute_query.assert_called_once()
        # Check that the query contains DISTINCT
        assert "DISTINCT" in mock_execute_query.call_args[0][0]

    @pytest.mark.asyncio
    @patch("src.database.repository.BaseRepository.execute_query")
    async def test_fetch_distinct_picktasks_error(self, mock_execute_query):
        """Test handling errors when fetching distinct picktasks."""
        # Arrange
        mock_execute_query.side_effect = Exception("Database error")
        repo = PicklistRepository()

        # Act/Assert
        with pytest.raises(QueryError) as excinfo:
            await repo.fetch_distinct_picktasks()

        assert "Failed to fetch distinct picktasks" in str(excinfo.value)

    @pytest.mark.asyncio
    @patch(
        "src.database.services.picklist.PicklistRepository.fetch_picklist_data"
    )
    @patch(
        "src.database.services.picklist.PicklistRepository.fetch_distinct_picktasks"
    )
    async def test_map_picklist_data(
        self, mock_fetch_distinct_picktasks, mock_fetch_picklist_data
    ):
        """Test mapping picklist data."""
        # Arrange
        # The implementation expects rows with specific indexes:
        # - row[0] = database ID
        # - row[3] = picktaskid
        # - row[21], row[22] = pick location coordinates
        # - row[67], row[68] = staging location coordinates

        # Create mock rows with the required structure
        mock_rows = []
        for i in range(3):
            row = {
                "id": f"id{i + 1}",
                "picktask_id": f"task{(i % 2) + 1}",
                "pick_loc_x": 10 + i * 10,
                "pick_loc_y": 20 + i * 10,
                "stage_loc_x": 50 + i * 10,
                "stage_loc_y": 60 + i * 10,
            }
            mock_rows.append(row)

        mock_fetch_picklist_data.return_value = mock_rows
        mock_fetch_distinct_picktasks.return_value = ["task1", "task2"]

        repo = PicklistRepository()

        # Act
        staging, taskid, id_mapping = await repo.map_picklist_data(
            WAREHOUSE_NAME
        )

        # Assert
        # Check that the dictionaries have the expected keys
        assert "task1" in staging
        assert "task2" in staging
        assert "task1" in taskid
        assert "task2" in taskid
        assert "task1" in id_mapping
        assert "task2" in id_mapping

        # Check that the dictionaries contain the expected data structure
        assert isinstance(staging["task1"], list)
        assert isinstance(staging["task2"], list)
        assert isinstance(taskid["task1"], list)
        assert isinstance(taskid["task2"], list)
        assert isinstance(id_mapping["task1"], str)
        assert isinstance(id_mapping["task2"], str)

        # Check the content of the dictionaries
        assert len(staging["task1"]) > 0
        assert len(taskid["task1"]) > 0
        assert id_mapping["task1"] == "id1"

    @pytest.mark.asyncio
    @patch(
        "src.database.services.picklist.PicklistRepository.map_picklist_data"
    )
    async def test_get_optimized_data_with_empty_data(
        self, mock_map_picklist_data
    ):
        """Test getting optimized data with empty input."""
        # Arrange
        mock_map_picklist_data.return_value = ({}, {}, {})
        repo = PicklistRepository()

        # Act
        result = await repo.get_optimized_data(WAREHOUSE_NAME)
        picktasks, orders_assign, stage_result, picklistids = result

        # Assert
        assert not picktasks
        assert not orders_assign
        assert not stage_result
        assert not picklistids

    @pytest.mark.asyncio
    @patch(
        "src.database.services.picklist.PicklistRepository.map_picklist_data"
    )
    async def test_get_optimized_data_with_multiple_tasks(
        self, mock_map_picklist_data
    ):
        """Test getting optimized data with multiple tasks."""
        # Arrange
        mock_map_picklist_data.return_value = (
            # staging
            {"task1": [(5, 5)], "task2": [(15, 15)], "task3": [(25, 25)]},
            # taskid
            {"task1": [(10, 20)], "task2": [(30, 40)], "task3": [(50, 60)]},
            # id_mapping
            {"task1": "id1", "task2": "id2", "task3": "id3"},
        )
        repo = PicklistRepository()

        # Act
        result = await repo.get_optimized_data(WAREHOUSE_NAME)
        picktasks, orders_assign, stage_result, picklistids = result

        # Assert
        assert len(picktasks) == 3
        assert "task1" in picktasks
        assert "task2" in picktasks
        assert "task3" in picktasks

        assert len(orders_assign) == 3
        assert orders_assign[0] == [(10, 20)]
        assert orders_assign[1] == [(30, 40)]
        assert orders_assign[2] == [(50, 60)]

        assert len(stage_result) == 3
        assert stage_result["task1"] == [(5, 5)]
        assert stage_result["task2"] == [(15, 15)]
        assert stage_result["task3"] == [(25, 25)]

        assert len(picklistids) == 3
        assert picklistids[0] == "id1"
        assert picklistids[1] == "id2"
        assert picklistids[2] == "id3"
