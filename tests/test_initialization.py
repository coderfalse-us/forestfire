"""Tests for the initialization functions.

This module contains tests for the population initialization functions used in
warehouse order picking optimization.
"""

import pytest
from forestfire.core.optimizer import WarehouseOptimizer
from forestfire.utils.config import WarehouseConfig, WarehouseConfigManager


class TestInitialization:
    """Test cases for the initialization functions."""

    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance with test configuration."""
        config = WarehouseConfig(
            num_pickers=3,
            picker_capacities=[10, 10, 10],
            picker_locations=[(0, 0), (10, 0), (20, 0)],
            warehouse_name="TEST",
        )
        optimizer = WarehouseOptimizer()
        optimizer.config = WarehouseConfigManager(config)
        return optimizer

    def test_initialize_population_size(self, optimizer):
        """Test initialize_population returns correct number of solutions."""
        # Arrange
        num_pickers = 3
        orders_size = 5
        picker_capacities = [10, 10, 10]

        # Act
        population = optimizer.initialize_population(
            num_pickers, orders_size, picker_capacities
        )

        # Assert
        assert len(population) > 0
        assert all(len(assignment) == orders_size for assignment in population)

    def test_initialize_population_picker_range(self, optimizer):
        """Test that initialize_population assigns valid picker IDs."""
        # Arrange
        num_pickers = 3
        orders_size = 5
        picker_capacities = [10, 10, 10]

        # Act
        population = optimizer.initialize_population(
            num_pickers, orders_size, picker_capacities
        )

        # Assert
        for assignment in population:
            assert all(0 <= picker_id < num_pickers for picker_id in assignment)

    def test_initialize_population_valid_assignments(self, optimizer):
        """Test that initialize_population respects capacity constraints."""
        # Arrange
        num_pickers = 3
        orders_size = 15
        picker_capacities = [5, 5, 5]

        # Act
        population = optimizer.initialize_population(
            num_pickers, orders_size, picker_capacities
        )

        # Assert
        for assignment in population:
            picker_counts = [assignment.count(i) for i in range(num_pickers)]
            assert all(
                count <= capacity
                for count, capacity in zip(picker_counts, picker_capacities)
            )

    def test_initialize_population_random_choice(self, optimizer):
        """Test that initialize_population uses random assignment."""
        # Arrange
        num_pickers = 3
        orders_size = 10
        picker_capacities = [10, 10, 10]

        # Act
        population1 = optimizer.initialize_population(
            num_pickers, orders_size, picker_capacities
        )
        population2 = optimizer.initialize_population(
            num_pickers, orders_size, picker_capacities
        )

        # Assert
        # Check that at least one assignment is different (randomness check)
        assert any(
            assignment1 != assignment2
            for assignment1, assignment2 in zip(population1, population2)
        )

    def test_initialize_population_with_limited_capacity(self, optimizer):
        """Test initialize_population with limited picker capacity."""
        # Arrange
        num_pickers = 2
        orders_size = 10
        # Picker 0 can only handle 3 items
        picker_capacities = [3, 7]

        # Act
        population = optimizer.initialize_population(
            num_pickers, orders_size, picker_capacities
        )

        # Assert
        for assignment in population:
            picker0_count = assignment.count(0)
            picker1_count = assignment.count(1)
            assert picker0_count <= picker_capacities[0]
            assert picker1_count <= picker_capacities[1]
