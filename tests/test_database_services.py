"""Tests for the database services.

This module contains tests for the database services used in
warehouse order picking optimization.
"""

import pytest
from unittest.mock import patch, MagicMock
from forestfire.database.services.picklist import PicklistRepository
from forestfire.database.services.batch_pick_seq_service import (
    BatchPickSequenceService,
)
from forestfire.database.services.picksequencemodel import PickSequenceUpdate
from forestfire.database.exceptions import QueryError
from forestfire.optimizer.models.route import Route

# Configure pytest-asyncio for async tests only
# We'll apply the mark to individual async tests instead of globally


class TestPicklistRepository:
    """Test cases for the PicklistRepository class."""

    @patch("forestfire.database.repository.BaseRepository.execute_query")
    def test_fetch_picklist_data(self, mock_execute_query):
        """Test fetching picklist data."""
        # Arrange
        mock_execute_query.return_value = [
            (1, "task1", 10, 20),
            (2, "task2", 30, 40),
        ]
        repo = PicklistRepository()

        # Act
        result = repo.fetch_picklist_data()

        # Assert
        assert result == mock_execute_query.return_value
        mock_execute_query.assert_called_once()

    @patch("forestfire.database.repository.BaseRepository.execute_query")
    def test_fetch_picklist_data_error(self, mock_execute_query):
        """Test handling errors when fetching picklist data."""
        # Arrange
        mock_execute_query.side_effect = Exception("Database error")
        repo = PicklistRepository()

        # Act/Assert
        with pytest.raises(QueryError):
            repo.fetch_picklist_data()

    @patch.object(PicklistRepository, "map_picklist_data")
    def test_get_optimized_data(self, mock_map_picklist_data):
        """Test getting optimized data."""
        # Arrange
        # Mock the map_picklist_data method to return test data
        mock_map_picklist_data.return_value = (
            # staging
            {"task1": [(5, 5)], "task2": [(15, 15)]},
            # taskid
            {"task1": [(10, 20)], "task2": [(30, 40)]},
            # id_mapping
            {"task1": "id1", "task2": "id2"},
        )
        repo = PicklistRepository()

        # Act
        (picktasks, orders_assign, stage_result, picklistids) = (
            repo.get_optimized_data()
        )

        # Assert
        assert len(picktasks) == 2
        assert len(orders_assign) == 2
        assert len(stage_result) == 2
        assert len(picklistids) == 2
        mock_map_picklist_data.assert_called_once()


class TestBatchPickSequenceService:
    """Test cases for the BatchPickSequenceService class."""

    @pytest.mark.asyncio
    @patch("forestfire.database.repository.BaseRepository.execute_query")
    @patch(
        "forestfire.optimizer.services.routing.RouteOptimizer.calculate_shortest_route"
    )
    @patch.object(BatchPickSequenceService, "send_sequence_update")
    async def test_update_pick_sequences(
        self,
        mock_send_update,  # pylint: disable=unused-argument
        mock_calculate_shortest_route,
        mock_execute_query,
    ):
        """Test updating pick sequences."""
        # Arrange
        # Mock the calculate_shortest_route method with proper Route objects
        mock_calculate_shortest_route.return_value = (
            100.0,
            [
                Route(
                    picker_id=0,
                    locations=[(0, 0), (10, 10)],
                    assigned_orders=[0],
                ),
                Route(
                    picker_id=1,
                    locations=[(10, 10), (20, 20)],
                    assigned_orders=[1],
                ),
            ],
            [[(0, 0), (10, 10)], [(10, 10), (20, 20)]],
        )

        # Mock the execute_query method with complete data for updates
        # Include all 7 expected columns: picklist_id,
        #  picktask_id, x, y, accountid, businessunitid, warehouseid
        mock_execute_query.return_value = [
            ("id1", "task1", 0, 0, "account1", "business1", "warehouse1"),
            ("id2", "task2", 10, 10, "account1", "business1", "warehouse1"),
        ]

        service = BatchPickSequenceService()
        final_solution = [0, 1]
        picklistids = ["id1", "id2"]
        orders_assign = [[(0, 0)], [(10, 10)]]
        picktasks = ["task1", "task2"]
        stage_result = {"task1": [(5, 5)], "task2": [(15, 15)]}

        # Act
        await service.update_pick_sequences(
            final_solution, picklistids, orders_assign, picktasks, stage_result
        )

        # Assert
        mock_calculate_shortest_route.assert_called_once()
        assert mock_execute_query.call_count >= 1
        # Check that send_sequence_update was called with non-empty updates
        mock_send_update.assert_called_once()

    def test_transform_updates_to_api_format(self):
        """Test transforming updates to API format."""
        # Arrange
        service = BatchPickSequenceService()
        updates = [
            PickSequenceUpdate(
                picklist_id="01JP45RZ36HTQFMH048DZD5F95",
                batch_id="BOBSBATCH",
                pick_sequence=222,
                picktask_id="TASK123",
                account_id="account1",
                business_unit_id="business1",
                warehouse_id="warehouse1",
            ),
            PickSequenceUpdate(
                picklist_id="01JP3WXZ33ENQHYAJC6S8R9YKP",
                batch_id=" BOBSBATCH ",  # Note the spaces to test strip()
                pick_sequence=3333,
                picktask_id="TASK123",
                account_id="account1",
                business_unit_id="business1",
                warehouse_id="warehouse1",
            ),
        ]

        # Act
        # pylint: disable=protected-access
        result = service._transform_updates_to_api_format(updates)

        # Assert
        assert hasattr(result[0], 'PickTasks')
        assert len(result[0].PickTasks) == 1
        # Both updates have same batch_id

        pick_task = result[0].PickTasks[0]
        assert pick_task.UserAssigned == "BOB"
        assert pick_task.Batch == "BOBSBATCH"
        assert hasattr(pick_task, 'AdditionalProperties')
        assert len(pick_task.PickLists) == 2

        # Check that the pick lists contain the correct data
        pick_lists = pick_task.PickLists
        assert any(
            pl.PickListId == "01JP45RZ36HTQFMH048DZD5F95"
            and pl.Sequence == 222
            and pl.Test == "PF03"
            for pl in pick_lists
        )
        assert any(
            pl.PickListId == "01JP3WXZ33ENQHYAJC6S8R9YKP"
            and pl.Sequence == 3333
            and pl.Test == "PF03"
            for pl in pick_lists
        )

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.put")
    @patch.object(BatchPickSequenceService, "_transform_updates_to_api_format")
    async def test_send_sequence_update(self, mock_transform, mock_put):
        """Test sending sequence updates to the API."""
        # Arrange
        service = BatchPickSequenceService()
        updates = [
            PickSequenceUpdate(
                picklist_id="01JP45RZ36HTQFMH048DZD5F95",
                batch_id="BOBSBATCH",
                pick_sequence=222,
                picktask_id="TASK123",
                account_id="account1",
                business_unit_id="business1",
                warehouse_id="warehouse1",
            )
        ]

        # Mock the transform method to return a list of ApiPayload objects
        from forestfire.database.services.picksequencemodel import ApiPayload, PickTaskPayload

        mock_api_data = [
            ApiPayload(
                AccountId="account1",
                BusinessunitId="business1",
                WarehouseId="warehouse1",
                PickTasks=[
                    PickTaskPayload(
                        TaskId="test",
                        Batch="BOBSBATCH",
                        PickLists=[]
                    )
                ]
            )
        ]
        mock_transform.return_value = mock_api_data

        # Mock the httpx response
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_put.return_value = mock_response

        # Act
        await service.send_sequence_update(updates)

        # Assert
        mock_transform.assert_called_once_with(updates)
        mock_put.assert_called_once()

        # Check that the API was called with the correct data
        call_kwargs = mock_put.call_args.kwargs
        assert call_kwargs["json"] == mock_api_data[0].model_dump()  # First item in the list, converted to dict
        assert "Authorization" in call_kwargs["headers"]
        assert call_kwargs["headers"]["Content-Type"] == "application/json"
        assert call_kwargs["headers"]["App-User-Id"] == "Forestfire"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.put")
    async def test_send_sequence_update_empty(self, mock_put):
        """Test sending empty sequence updates to the API."""
        # Arrange
        service = BatchPickSequenceService()

        # Act
        await service.send_sequence_update([])

        # Assert
        mock_put.assert_not_called()
