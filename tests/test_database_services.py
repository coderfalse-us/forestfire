"""Tests for the database services.

This module contains tests for the database services used in
warehouse order picking optimization.
"""

import pytest
from unittest.mock import patch, MagicMock
from forestfire.database.services.picklist import PicklistRepository
from forestfire.database.services.batch_pick_seq_service import BatchPickSequenceService
from forestfire.database.exceptions import QueryError

class TestPicklistRepository:
    """Test cases for the PicklistRepository class."""

    @patch('forestfire.database.repository.BaseRepository.execute_query')
    def test_fetch_picklist_data(self, mock_execute_query):
        """Test fetching picklist data."""
        # Arrange
        mock_execute_query.return_value = [
            (1, 'task1', 10, 20),
            (2, 'task2', 30, 40)
        ]
        repo = PicklistRepository()

        # Act
        result = repo.fetch_picklist_data()

        # Assert
        assert result == mock_execute_query.return_value
        mock_execute_query.assert_called_once()

    @patch('forestfire.database.repository.BaseRepository.execute_query')
    def test_fetch_picklist_data_error(self, mock_execute_query):
        """Test handling errors when fetching picklist data."""
        # Arrange
        mock_execute_query.side_effect = Exception('Database error')
        repo = PicklistRepository()

        # Act/Assert
        with pytest.raises(QueryError):
            repo.fetch_picklist_data()

    @patch.object(PicklistRepository, 'map_picklist_data')
    def test_get_optimized_data(self, mock_map_picklist_data):
        """Test getting optimized data."""
        # Arrange
        # Mock the map_picklist_data method to return test data
        mock_map_picklist_data.return_value = (
            # staging
            {'task1': [(5, 5)], 'task2': [(15, 15)]},
            # taskid
            {'task1': [(10, 20)], 'task2': [(30, 40)]},
            # id_mapping
            {'task1': 'id1', 'task2': 'id2'}
        )
        repo = PicklistRepository()

        # Act
        (picktasks, orders_assign, stage_result,
         picklistids) = repo.get_optimized_data()

        # Assert
        assert len(picktasks) == 2
        assert len(orders_assign) == 2
        assert len(stage_result) == 2
        assert len(picklistids) == 2
        mock_map_picklist_data.assert_called_once()


class TestBatchPickSequenceService:
    """Test cases for the BatchPickSequenceService class."""

    @patch('forestfire.database.repository.BaseRepository.execute_query')
    @patch('forestfire.optimizer.services.routing.RouteOptimizer.calculate_shortest_route')
    def test_update_pick_sequences(self, mock_calculate_shortest_route,
                                 mock_execute_query):
        """Test updating pick sequences."""
        # Arrange
        # Mock the calculate_shortest_route method
        mock_calculate_shortest_route.return_value = (
            100.0,
            [
                MagicMock(picker_id=0, locations=[(0, 0), (10, 10)],
                         assigned_orders=[0]),
                MagicMock(picker_id=1, locations=[(10, 10), (20, 20)],
                         assigned_orders=[1])
            ],
            []
        )

        # Mock the execute_query method
        mock_execute_query.return_value = [
            ('id1', 'task1', 10, 20),
            ('id2', 'task2', 30, 40)
        ]

        service = BatchPickSequenceService()
        final_solution = [0, 1]
        picklistids = ['id1', 'id2']
        orders_assign = [[(10, 20)], [(30, 40)]]
        picktasks = ['task1', 'task2']
        stage_result = {'task1': [(5, 5)], 'task2': [(15, 15)]}

        # Act
        service.update_pick_sequences(
            final_solution, picklistids, orders_assign, picktasks, stage_result
        )

        # Assert
        mock_calculate_shortest_route.assert_called_once()
        assert mock_execute_query.call_count >= 1
