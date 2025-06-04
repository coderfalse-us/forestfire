"""Tests for the graph visualization module.

This module contains tests for the path visualization functionality used in
warehouse order picking optimization.
"""

import pytest
from unittest.mock import patch, MagicMock
from forestfire.plots.graph import PathVisualizer
from forestfire.optimizer.models.route import Route
# pylint: disable=redefined-outer-name


@pytest.fixture
def sample_config():
    """Fixture for warehouse configuration."""

    class Config:
        NUM_PICKERS = 3
        PICKER_CAPACITIES = [5, 5, 5]
        PICKER_LOCATIONS = [(0, 0), (10, 10), (20, 20)]
        WAREHOUSE_NAME = "warehouse_1"

    return Config()


class TestPathVisualizer:
    """Test cases for the PathVisualizer class."""

    @pytest.mark.asyncio
    @patch("forestfire.plots.graph.PathVisualizer.save_plot")
    async def test_plot_routes(
        self, mock_save_plot, path_visualizer, sample_config
    ):
        """Test plotting routes."""
        # Arrange
        solution = [0, 1, 2, 0, 1]
        mock_save_plot.return_value = "test_path.png"

        # Mock the calculate_shortest_route method
        path_visualizer.route_optimizer.calculate_shortest_route = MagicMock(
            return_value=(
                100.0,
                [
                    Route(
                        picker_id=0,
                        locations=[(0, 0), (10, 10)],
                        cost=14.14,
                        assigned_orders=[0, 3],
                    ),
                    Route(
                        picker_id=1,
                        locations=[(10, 10), (20, 20)],
                        cost=14.14,
                        assigned_orders=[1, 4],
                    ),
                    Route(
                        picker_id=2,
                        locations=[(20, 20), (30, 30)],
                        cost=14.14,
                        assigned_orders=[2],
                    ),
                ],
                [
                    [(0, 0), (10, 10)],
                    [(10, 10), (20, 20)],
                    [(20, 20), (30, 30)],
                ],
            )
        )

        # Mock the get_optimized_data method
        path_visualizer.picklist_repo.get_optimized_data = MagicMock(
            return_value=(
                ["task1", "task2", "task3", "task4", "task5"],
                [[(10, 20)], [(30, 40)], [(50, 60)], [(70, 80)], [(90, 100)]],
                {"task1": [(5, 5)]},
                ["id1", "id2", "id3", "id4", "id5"],
            )
        )
        config = sample_config
        # Act
        result = await path_visualizer.plot_routes(solution, config)

        # Assert
        assert result == "test_path.png"
        mock_save_plot.assert_called_once()

    @pytest.mark.asyncio
    @patch("forestfire.plots.graph.PathVisualizer.save_plot")
    async def test_plot_routes_with_empty_solution(
        self, mock_save_plot, path_visualizer, sample_config
    ):
        """Test plotting routes with an empty solution."""
        # Arrange
        solution = []
        mock_save_plot.return_value = "test_path.png"

        # Mock the get_optimized_data method
        path_visualizer.picklist_repo.get_optimized_data = MagicMock(
            return_value=([], [], {}, [])
        )

        config = sample_config

        # Act
        result = await path_visualizer.plot_routes(solution, config)

        # Assert
        assert result == "test_path.png"
        mock_save_plot.assert_called_once()

    def test_save_plot(self, path_visualizer):
        """Test saving a plot."""
        # Arrange
        with patch("matplotlib.pyplot.savefig") as mock_savefig:
            # Act
            result = path_visualizer.save_plot("test_plot")

            # Assert
            assert "test_plot_" in result
            assert result.endswith(".png")
            mock_savefig.assert_called_once()

    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_output_directory_creation(self, mock_makedirs, mock_exists):
        """Test that the output directory is created if it doesn't exist."""
        # Arrange
        mock_exists.return_value = False

        # Act
        # pylint: disable=unused-variable
        visualizer = PathVisualizer()  # noqa

        # Assert
        mock_makedirs.assert_called_once()
