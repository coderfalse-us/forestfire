"""Tests for the genetic algorithm module.

This module contains tests for the genetic algorithm operations used in
warehouse order picking optimization.
"""

from src.utils.config import (
    TEST_PICKER_CAPACITIES as PICKER_CAPACITIES,
    TEST_NUM_PICKERS as NUM_PICKERS,
)


class TestGeneticOperator:
    """Test cases for the GeneticOperator class."""

    def test_crossover_produces_valid_offspring(self, genetic_operator):
        """Test that crossover produces valid offspring."""
        # Arrange
        parent1 = [0, 1, 2, 0, 1]
        parent2 = [1, 0, 2, 1, 0]

        # Act
        offspring1, offspring2 = genetic_operator.crossover(
            parent1, parent2, PICKER_CAPACITIES, NUM_PICKERS
        )

        # Assert
        assert len(offspring1) == len(parent1)
        assert len(offspring2) == len(parent2)
        assert all(0 <= picker_id < NUM_PICKERS for picker_id in offspring1)
        assert all(0 <= picker_id < NUM_PICKERS for picker_id in offspring2)

    def test_enforce_capacity_constraints(self, genetic_operator):
        """Test that capacity constraints are enforced."""
        # Arrange
        # Exceeds capacity for picker 0
        assignment = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        picker_capacities = [10] * NUM_PICKERS

        # Act
        # pylint: disable=protected-access
        result = genetic_operator._enforce_capacity_constraints(
            assignment, picker_capacities, NUM_PICKERS
        )

        # Assert
        picker_counts = [result.count(i) for i in range(NUM_PICKERS)]
        assert all(
            count <= capacity
            for count, capacity in zip(picker_counts, picker_capacities)
        )

    def test_mutate_with_capacity(self, genetic_operator):
        """Test mutation with capacity constraints."""
        # Arrange
        assignment = [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]

        # Act
        result = genetic_operator.mutate_with_capacity(
            assignment, PICKER_CAPACITIES, NUM_PICKERS
        )

        # Assert
        assert len(result) == len(assignment)
        assert all(0 <= picker_id < NUM_PICKERS for picker_id in result)

        # Check that capacity constraints are respected
        picker_counts = [result.count(i) for i in range(NUM_PICKERS)]
        assert all(
            count <= capacity
            for count, capacity in zip(picker_counts, PICKER_CAPACITIES)
        )

    def test_tournament_selection(self, genetic_operator, sample_population):
        """Test tournament selection."""
        # Arrange
        tournament_size = 3

        # Act
        selected = genetic_operator.tournament_selection(
            sample_population, tournament_size
        )

        # Assert
        assert selected in [item[0] for item in sample_population]

    def test_single_point_crossover(self, genetic_operator):
        """Test single point crossover."""
        # Arrange
        parent1 = [0, 1, 2, 0, 1]
        parent2 = [1, 0, 2, 1, 0]

        # Act
        # pylint: disable=protected-access
        offspring1, offspring2 = genetic_operator._single_point_crossover(
            parent1, parent2
        )

        # Assert
        assert len(offspring1) == len(parent1)
        assert len(offspring2) == len(parent2)

        # Check that offspring are different from parents
        assert offspring1 != parent1 or offspring1 != parent2
        assert offspring2 != parent1 or offspring2 != parent2

    def test_uniform_crossover(self, genetic_operator):
        """Test uniform crossover."""
        # Arrange
        parent1 = [0, 1, 2, 0, 1]
        parent2 = [1, 0, 2, 1, 0]

        # Act
        # pylint: disable=protected-access
        offspring1, offspring2 = genetic_operator._uniform_crossover(
            parent1, parent2
        )

        # Assert
        assert len(offspring1) == len(parent1)
        assert len(offspring2) == len(parent2)

        # Check that each gene in offspring comes from either parent1 or parent2
        for i in range(len(offspring1)):
            assert offspring1[i] in [parent1[i], parent2[i]]
            assert offspring2[i] in [parent1[i], parent2[i]]
