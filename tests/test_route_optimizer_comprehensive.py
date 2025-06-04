"""Tests for the RouteOptimizer class.

This module contains comprehensive tests for the RouteOptimizer class
used for route optimization in the warehouse order picking optimization.
"""

from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.optimizer.models.route import Route


class TestRouteOptimizerComprehensive:
    """Comprehensive test cases for the RouteOptimizer class."""

    def test_calculate_route_cost_with_multiple_locations(self):
        """Test calculating route cost with multiple locations."""
        # Arrange
        optimizer = RouteOptimizer()
        path = [(0, 0), (10, 10), (20, 20), (30, 30)]

        # Act
        # The method is protected (_calculate_route_cost)
        cost = optimizer._calculate_route_cost(path)

        # Assert
        # Expected cost: sqrt(10^2 + 10^2) * 3 = 14.14 * 3
        expected_cost = 14.14 * 3
        assert abs(cost - expected_cost) < 0.1

    def test_calculate_route_cost_with_single_location(self):
        """Test calculating route cost with a single location."""
        # Arrange
        optimizer = RouteOptimizer()
        path = [(10, 10)]

        # Act
        # The method is protected (_calculate_route_cost)
        cost = optimizer._calculate_route_cost(path)

        # Assert
        assert cost == 0  # No movement, so cost is 0

    def test_calculate_route_cost_with_empty_path(self):
        """Test calculating route cost with an empty path."""
        # Arrange
        optimizer = RouteOptimizer()
        path = []

        # Act
        # The method is protected (_calculate_route_cost)
        cost = optimizer._calculate_route_cost(path)

        # Assert
        assert cost == 0  # Empty path, so cost is 0

    def test_calculate_shortest_route_with_valid_assignment(self):
        """Test calculating shortest route with a valid assignment."""
        # Arrange
        optimizer = RouteOptimizer()
        picker_locations = [(0, 0), (10, 10)]  # Locations for 2 pickers
        # 3 orders to picker 0, 2 orders to picker 1
        assignment = [0, 1, 0, 1, 0]
        orders_assign = [
            [(0, 0)],  # Order 0 location
            [(10, 10)],  # Order 1 location
            [(20, 20)],  # Order 2 location
            [(30, 30)],  # Order 3 location
            [(40, 40)],  # Order 4 location
        ]
        picktasks = ["task1", "task2", "task3", "task4", "task5"]
        stage_result = {
            "task1": [(5, 5)],
            "task2": [(15, 15)],
            "task3": [(25, 25)],
            "task4": [(35, 35)],
            "task5": [(45, 45)],
        }
        num_pickers = 2

        # Act
        total_cost, routes, paths = optimizer.calculate_shortest_route(
            num_pickers,
            picker_locations,
            assignment,
            orders_assign,
            picktasks,
            stage_result,
        )

        # Assert
        assert isinstance(total_cost, float)
        assert len(routes) == len(picker_locations)
        assert all(isinstance(route, Route) for route in routes)

        # Check that the routes have the correct picker_id
        assert routes[0].picker_id == 0
        assert routes[1].picker_id == 1

        # Check that the routes have the correct assigned_orders
        assert len(routes[0].assigned_orders) > 0  # Picker 0 has assignments
        assert len(routes[1].assigned_orders) > 0  # Picker 1 has assignments

        # Check that the paths are returned
        assert len(paths) == len(picker_locations)
        assert all(isinstance(path, list) for path in paths)

    def test_calculate_shortest_route_with_empty_assignment(self):
        """Test calculating shortest route with an empty assignment."""
        # Arrange
        optimizer = RouteOptimizer()
        picker_locations = [(0, 0), (10, 10)]  # Locations for 2 pickers
        assignment = []
        orders_assign = []
        picktasks = []
        stage_result = {}
        num_pickers = 2

        # Act
        total_cost, routes, paths = optimizer.calculate_shortest_route(
            num_pickers,
            picker_locations,
            assignment,
            orders_assign,
            picktasks,
            stage_result,
        )

        # Assert
        assert total_cost == 0
        assert len(routes) == len(picker_locations)
        assert all(isinstance(route, Route) for route in routes)
        assert all(len(route.assigned_orders or []) == 0 for route in routes)
        assert len(paths) == len(picker_locations)

    def test_calculate_shortest_route_with_single_picker(self):
        """Test calculating shortest route with all orders to one picker."""
        # Arrange
        optimizer = RouteOptimizer()
        picker_locations = [(0, 0), (10, 10)]  # Locations for 2 pickers
        assignment = [0, 0, 0, 0, 0]  # All orders to picker 0
        orders_assign = [
            [(0, 0)],  # Order 0 location
            [(10, 10)],  # Order 1 location
            [(20, 20)],  # Order 2 location
            [(30, 30)],  # Order 3 location
            [(40, 40)],  # Order 4 location
        ]
        picktasks = ["task1", "task2", "task3", "task4", "task5"]
        stage_result = {
            "task1": [(5, 5)],
            "task2": [(15, 15)],
            "task3": [(25, 25)],
            "task4": [(35, 35)],
            "task5": [(45, 45)],
        }
        num_pickers = 2

        # Act
        total_cost, routes, _ = optimizer.calculate_shortest_route(
            num_pickers,
            picker_locations,
            assignment,
            orders_assign,
            picktasks,
            stage_result,
        )

        # Assert
        assert isinstance(total_cost, float)
        assert len(routes) == len(picker_locations)

        # Check that picker 0 has orders
        assert len(routes[0].assigned_orders or []) > 0

        # Check that other pickers have no orders
        for i in range(1, len(picker_locations)):
            assert len(routes[i].assigned_orders or []) == 0

    def test_calculate_shortest_route_with_complex_paths(self):
        """Test route calculation with complex paths and staging areas."""
        # Arrange
        optimizer = RouteOptimizer()
        picker_locations = [(0, 0), (10, 10)]  # Locations for 2 pickers
        # 3 orders to picker 0, 2 orders to picker 1
        assignment = [0, 1, 0, 1, 0]
        orders_assign = [
            [(0, 0), (5, 5)],  # Order 0 has multiple locations
            [(10, 10), (15, 15)],  # Order 1 has multiple locations
            [(20, 20)],  # Order 2 has a single location
            [(30, 30), (35, 35)],  # Order 3 has multiple locations
            [(40, 40)],  # Order 4 has a single location
        ]
        picktasks = ["task1", "task2", "task3", "task4", "task5"]
        stage_result = {
            "task1": [(50, 50), (55, 55)],  # Multiple staging locations
            "task2": [(60, 60)],
            "task3": [(70, 70), (75, 75)],  # Multiple staging locations
            "task4": [(80, 80)],
            "task5": [(90, 90)],
        }
        num_pickers = 2

        # Act
        total_cost, routes, paths = optimizer.calculate_shortest_route(
            num_pickers,
            picker_locations,
            assignment,
            orders_assign,
            picktasks,
            stage_result,
        )

        # Assert
        assert isinstance(total_cost, float)
        assert len(routes) == len(picker_locations)

        # Check that the routes include locations
        assert len(routes[0].locations) > 0
        assert len(routes[1].locations) > 0

        # Check that the paths include locations
        assert len(paths) == len(picker_locations)
        assert len(paths[0]) > 0
        assert len(paths[1]) > 0

    def test_calculate_shortest_route_with_multiple_pickers(self):
        """Test calculating shortest route with multiple pickers."""
        # Arrange
        optimizer = RouteOptimizer()
        picker_locations = [(0, 0), (10, 10)]  # Locations for 2 pickers
        assignment = [0, 1, 0, 1, 0]  # Mixed assignments
        orders_assign = [
            [(0, 0)],
            [(10, 10)],
            [(20, 20)],
            [(30, 30)],
            [(40, 40)],
        ]
        picktasks = ["task1", "task2", "task3", "task4", "task5"]
        stage_result = {
            "task1": [(5, 5)],
            "task2": [(15, 15)],
            "task3": [(25, 25)],
            "task4": [(35, 35)],
            "task5": [(45, 45)],
        }
        num_pickers = 2

        # Act
        total_cost, routes, paths = optimizer.calculate_shortest_route(
            num_pickers,
            picker_locations,
            assignment,
            orders_assign,
            picktasks,
            stage_result,
        )

        # Assert
        assert isinstance(total_cost, float)
        assert len(routes) == len(picker_locations)
        assert len(paths) == len(picker_locations)
