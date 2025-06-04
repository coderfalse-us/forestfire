"""Tests for the ant colony optimization module.

This module contains tests for the ant colony optimization algorithm used in
warehouse order picking optimization.
"""

import numpy as np
from forestfire.utils.config import (
    TEST_NUM_PICKERS as NUM_PICKERS,
    TEST_PICKER_CAPACITIES as PICKER_CAPACITIES,
)


class TestAntColonyOptimizer:
    """Test cases for the AntColonyOptimizer class."""

    def test_calculate_heuristic(
        self, ant_colony_optimizer, sample_orders_assign
    ):
        """Test heuristic calculation."""
        # Arrange
        picker_locations = [(0, 0), (10, 10), (20, 20)]

        # Act
        heuristic = ant_colony_optimizer.calculate_heuristic(
            sample_orders_assign, picker_locations
        )

        # Assert
        assert heuristic.shape == (
            len(sample_orders_assign),
            len(picker_locations),
        )
        assert np.all(heuristic > 0)  # Heuristic values should be positive

    def test_build_solution(
        self, ant_colony_optimizer, sample_pheromone, sample_heuristic
    ):
        """Test building a solution."""
        # Arrange
        orders_size = 5

        # Act
        assignment = ant_colony_optimizer.build_solution(
            sample_pheromone,
            sample_heuristic,
            orders_size,
            PICKER_CAPACITIES,
            NUM_PICKERS,
        )

        # Assert
        assert len(assignment) == orders_size
        assert all(0 <= picker_id < NUM_PICKERS for picker_id in assignment)

        # Check that capacity constraints are respected
        picker_counts = [assignment.count(i) for i in range(NUM_PICKERS)]
        assert all(
            count <= capacity
            for count, capacity in zip(picker_counts, PICKER_CAPACITIES)
        )

    def test_update_pheromone(self, ant_colony_optimizer, sample_pheromone):
        """Test pheromone update."""
        # Arrange
        assignment = [0, 1, 2, 0, 1]
        fitness_score = 100.0
        orders_size = 5
        initial_pheromone = sample_pheromone.copy()

        # Act
        ant_colony_optimizer.update_pheromone(
            sample_pheromone, assignment, fitness_score, orders_size
        )

        # Assert
        # Pheromone should be updated for assigned items
        for item in range(orders_size):
            picker = assignment[item]
            assert (
                sample_pheromone[item][picker]
                != initial_pheromone[item][picker]
            )

        # Pheromone for unassigned items should remain unchanged
        for item in range(orders_size):
            for picker in range(NUM_PICKERS):
                if picker != assignment[item]:
                    assert (
                        sample_pheromone[item][picker]
                        == initial_pheromone[item][picker]
                    )

    def test_build_solution_with_full_pickers(
        self, ant_colony_optimizer, sample_pheromone, sample_heuristic
    ):
        """Test building a solution when some pickers are at full capacity."""
        # Arrange
        orders_size = 5
        # Very limited capacity
        limited_capacities = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        # Act
        assignment = ant_colony_optimizer.build_solution(
            sample_pheromone,
            sample_heuristic,
            orders_size,
            limited_capacities,
            NUM_PICKERS,
        )

        # Assert
        assert len(assignment) == orders_size

        # Check that capacity constraints are respected
        picker_counts = [assignment.count(i) for i in range(NUM_PICKERS)]
        assert all(
            count <= capacity
            for count, capacity in zip(picker_counts, limited_capacities)
        )

        # Some items might be unassigned (-1) if all pickers are at capacity
        assert all(
            picker_id == -1 or (0 <= picker_id < NUM_PICKERS)
            for picker_id in assignment
        )
