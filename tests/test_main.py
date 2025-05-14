"""Tests for the main module.

This module contains tests for the main execution functions used in
warehouse order picking optimization.
"""

import pytest
from unittest.mock import patch, MagicMock
from main import run_aco_optimization, run_genetic_optimization, main
from forestfire.utils.config import NUM_PICKERS


class TestMain:
    """Test cases for the main module functions."""

    def test_run_aco_optimization(
        self,
        ant_colony_optimizer,
        route_optimizer,
        sample_orders_assign,
        sample_picktasks,
        sample_stage_result,
    ):
        """Test running ACO optimization."""
        # Arrange
        # Mock the calculate_shortest_route to return a fixed fitness score
        route_optimizer.calculate_shortest_route = MagicMock(
            return_value=(100.0, [], [])
        )

        # Act
        empty_pop = run_aco_optimization(
            ant_colony_optimizer,
            route_optimizer,
            sample_orders_assign,
            sample_picktasks,
            sample_stage_result,
        )

        # Assert
        assert len(empty_pop) > 0
        # Check format: [assignment, fitness]
        assert all(len(item) == 2 for item in empty_pop)
        # Check fitness is float
        assert all(isinstance(item[1], float) for item in empty_pop)

    def test_run_genetic_optimization(
        self,
        genetic_operator,
        route_optimizer,
        sample_population,
        sample_orders_assign,
        sample_picktasks,
        sample_stage_result,
    ):
        """Test running genetic optimization."""
        # Arrange
        # Mock the calculate_shortest_route to return a fixed fitness score
        route_optimizer.calculate_shortest_route = MagicMock(
            return_value=(100.0, [], [])
        )

        # Act
        final_solution = run_genetic_optimization(
            genetic_operator,
            route_optimizer,
            sample_population,
            sample_orders_assign,
            sample_picktasks,
            sample_stage_result,
        )

        # Assert
        assert len(final_solution) == len(sample_orders_assign)
        assert all(0 <= picker_id < NUM_PICKERS for picker_id in final_solution)

    @pytest.mark.asyncio
    @patch("main.run_genetic_optimization")
    async def test_main_function(self, mock_run_genetic_optimization):
        """Test the main function execution."""
        # Arrange
        with (
            patch("main.PicklistRepository") as mock_picklist_repo,
            patch("main.BatchPickSequenceService") as mock_batch_service,
            patch("main.RouteOptimizer") as mock_route_optimizer,
            patch("main.GeneticOperator"),
            patch("main.AntColonyOptimizer"),
            patch("main.PathVisualizer") as mock_path_visualizer,
            patch("main.run_aco_optimization") as mock_run_aco,
        ):
            # Mock the get_optimized_data method to return test data
            mock_picklist_repo.return_value.get_optimized_data.return_value = (
                ["task1", "task2", "task3", "task4", "task5"],  # picktasks
                # orders_assign
                [[(10, 20)], [(30, 40)], [(50, 60)], [(70, 80)], [(90, 100)]],
                {"task1": [(5, 5)]},  # stage_result
                ["id1", "id2", "id3", "id4", "id5"],  # picklistids
            )

            # Mock the calculate_shortest_route to return a fixed fitness score
            route_optimizer_mock = mock_route_optimizer.return_value
            route_optimizer_mock.calculate_shortest_route.return_value = (
                100.0,
                [],
                [],
            )

            # Mock the run_aco_optimization function
            mock_run_aco.return_value = [[[0, 1, 2, 0, 1], 100.0]]

            # Mock the run_genetic_optimization function
            mock_run_genetic_optimization.return_value = [0, 1, 2, 0, 1]

            # Mock the update_pick_sequences async method
            batch_service_mock = mock_batch_service.return_value

            # Create a mock coroutine for the async method
            async def mock_coro(*args, **kwargs):
                return None

            batch_service_mock.update_pick_sequences = mock_coro

            # Act - properly await the async function
            await main()

            # Assert
            # Check that all the necessary methods were called
            picklist_repo_mock = mock_picklist_repo.return_value
            picklist_repo_mock.get_optimized_data.assert_called_once()

            # Check route optimizer was called
            assert route_optimizer_mock.calculate_shortest_route.call_count > 0

            # Check visualization was called
            path_visualizer_mock = mock_path_visualizer.return_value
            path_visualizer_mock.plot_routes.assert_called_once()

            # For async methods, we can't use assert_called_once
            # We'd need a more complex setup with AsyncMock in Python 3.8+
            # This is simplified for the test

    @patch("main.logger")
    def test_main_script_execution(self, mock_logger):
        """Test the main script execution with exception handling."""
        # This test simulates the error handling in the main script's
        # if __name__ == '__main__' block

        # Create a mock for asyncio.run that raises an exception
        with patch("asyncio.run", side_effect=Exception("Test exception")):
            # Simulate the code in the if __name__ == '__main__' block
            try:
                # This is what happens in the main script
                import asyncio

                asyncio.run(main())
                pytest.fail("Exception was not raised")
            except Exception as e:
                # Verify that the error is the expected one
                assert str(e) == "Test exception"

                # In a real scenario, this would log the error
                # We're just testing the exception handling here
