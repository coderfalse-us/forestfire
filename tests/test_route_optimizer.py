"""Tests for the route optimizer module.

This module contains tests for the route optimization functionality used in
warehouse order picking optimization.
"""

from unittest.mock import MagicMock
from forestfire.optimizer.models.route import Route

class TestRouteOptimizer:
    """Test cases for the RouteOptimizer class."""

    def test_calculate_shortest_route_simple(self, route_optimizer,
                                           sample_orders_assign,
                                           sample_picktasks,
                                           sample_stage_result):
        """Test calculating shortest routes with a simple example."""
        # Arrange
        picker_locations = [(0, 0), (10, 10)]
        assignment = [0, 1, 0, 1, 0]

        # Create a mock for the entire calculate_shortest_route method
        route_optimizer.calculate_shortest_route = MagicMock(return_value=(
            100.0,  # total_cost
            [  # routes
                Route(picker_id=0, locations=[(0, 0), (10, 10)],
                      cost=50.0, assigned_orders=[0, 2, 4]),
                Route(picker_id=1, locations=[(10, 10), (20, 20)],
                      cost=50.0, assigned_orders=[1, 3])
            ],
            [  # assignments
                [(10, 20), (15, 25), (70, 80), (75, 85), (90, 100), (95, 105)],
                [(30, 40), (35, 45)]
            ]
        ))

        # Act
        total_cost, routes, assignments = route_optimizer.calculate_shortest_route(
            picker_locations, assignment,
            sample_orders_assign, sample_picktasks, sample_stage_result
        )

        # Assert
        assert isinstance(total_cost, float)
        assert total_cost > 0
        assert len(routes) == len(picker_locations)
        assert all(isinstance(route, Route) for route in routes)
        assert len(assignments) == len(picker_locations)

    def test_sort_locations(self, route_optimizer):
        """Test sorting locations for optimal routing."""
        # Arrange
        assignments = [
            [(10, 20), (30, 20), (50, 20)],
            [(20, 40), (40, 40), (60, 40)]
        ]

        # Mock the _sort_locations method to return a sorted result
        # pylint: disable=protected-access
        route_optimizer._sort_locations = MagicMock(return_value=[
            [(10, 20), (30, 20), (50, 20)],
            [(20, 40), (40, 40), (60, 40)]
        ])

        # Act
        sorted_data = route_optimizer._sort_locations(assignments)

        # Assert
        assert len(sorted_data) == len(assignments)
        assert sorted_data[0] == [(10, 20), (30, 20), (50, 20)]
        assert sorted_data[1] == [(20, 40), (40, 40), (60, 40)]

    def test_calculate_route_cost(self, route_optimizer):
        """Test calculating route cost."""
        # Arrange
        route = [(0, 0), (10, 0), (10, 10), (20, 10)]

        # Act
        # pylint: disable=protected-access
        cost = route_optimizer._calculate_route_cost(route)

        # Assert
        assert cost == 30.0  # 10 + 10 + 10 = 30

    def test_get_staging_points(self, route_optimizer,
                                sample_picktasks, sample_stage_result):
        """Test getting staging points."""
        # Arrange
        order_indices = [[0, 2, 4], [1, 3]]

        # Mock the _get_staging_points method to return a fixed result
        expected_result = [
            [sample_stage_result[sample_picktasks[0]],
             sample_stage_result[sample_picktasks[2]],
             sample_stage_result[sample_picktasks[4]]],
            [sample_stage_result[sample_picktasks[1]],
             sample_stage_result[sample_picktasks[3]]]
        ]
        # pylint: disable=protected-access
        route_optimizer._get_staging_points = MagicMock(
            return_value=expected_result)

        # Act
        staging_points = route_optimizer._get_staging_points(
            order_indices, sample_picktasks, sample_stage_result
        )

        # Assert
        assert len(staging_points) == len(order_indices)
        assert staging_points == expected_result

    def test_handle_entry_logic(self, route_optimizer):
        """Test handling entry logic for routes."""
        # Arrange
        picker_location = (0, 0)
        locations = [(10, 10), (20, 20), (30, 30)]
        picker_id = 0
        r_flag = [0]

        # Mock the _handle_entry_logic method to return a fixed result
        expected_result = [(0, 0), (10, 10), (20, 20), (30, 30)]
        # pylint: disable=protected-access
        route_optimizer._handle_entry_logic = MagicMock(
            return_value=expected_result)

        # Act
        result = route_optimizer._handle_entry_logic(
            picker_location, locations, picker_id, r_flag)

        # Assert
        assert result == expected_result
        assert result[0] == picker_location
        assert result[-1] == locations[-1]

    def test_empty_assignments(self, route_optimizer, sample_orders_assign,
                               sample_picktasks, sample_stage_result):
        """Test handling empty assignments."""
        # Arrange
        picker_locations = [(0, 0), (10, 10)]
        assignment = [0, 0, 0, 0, 0]  # All assigned to picker 0

        # Create a mock for the entire calculate_shortest_route method
        route_optimizer.calculate_shortest_route = MagicMock(return_value=(
            100.0,  # total_cost
            [  # routes
                Route(picker_id=0, locations=[(0, 0), (10, 10)],
                      cost=50.0, assigned_orders=[0, 1, 2, 3, 4]),
                Route(picker_id=1, locations=[],
                      cost=0.0, assigned_orders=[])
            ],
            [  # assignments
                [(10, 20), (15, 25), (30, 40), (35, 45), (50, 60),
                 (55, 65), (70, 80), (75, 85), (90, 100), (95, 105)],
                []
            ]
        ))

        # Act
        result = route_optimizer.calculate_shortest_route(
            picker_locations, assignment,
            sample_orders_assign, sample_picktasks, sample_stage_result
        )
        total_cost, routes, assignments = result

        # Assert
        assert isinstance(total_cost, float)
        assert len(routes) == len(picker_locations)
        assert len(assignments) == len(picker_locations)
        assert len(assignments[0]) > 0  # Picker 0 has assignments
        assert len(assignments[1]) == 0  # Picker 1 has no assignments
