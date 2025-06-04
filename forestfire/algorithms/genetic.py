"""Genetic algorithm implementation for warehouse order picking optimization.

This module provides genetic operators for crossover, mutation, and selection
to optimize picker routes in a warehouse environment.
"""

import random
import numpy as np
from typing import List, Tuple
from forestfire.utils.config import PC
from forestfire.optimizer.services.routing import RouteOptimizer


class GeneticOperator:
    """Class for genetic algorithm operations"""

    def __init__(self, route_optimizer: RouteOptimizer):
        self.route_optimizer = route_optimizer

    def crossover(
        self,
        x1: List[int],
        x2: List[int],
        picker_capacities: List[int],
        num_pickers: int,
    ) -> Tuple[List[int], List[int]]:
        """Perform crossover between two parent solutions"""
        q = random.uniform(0, 1)

        if q <= PC:
            g = random.randint(1, 2)
            if g == 1:
                y1, y2 = self._single_point_crossover(x1, x2)
            else:
                y1, y2 = self._uniform_crossover(x1, x2)

            # Ensure offspring satisfy picker capacity constraints
            y1 = self._enforce_capacity_constraints(
                y1, picker_capacities, num_pickers
            )
            y2 = self._enforce_capacity_constraints(
                y2, picker_capacities, num_pickers
            )
        else:
            y1 = x1[:]
            y2 = x2[:]

        return y1, y2

    def _single_point_crossover(
        self, x1: List[int], x2: List[int]
    ) -> Tuple[List[int], List[int]]:
        """Perform single point crossover"""
        n = len(x1)
        crossover_point = random.randint(1, n - 1)

        y1 = x1[:crossover_point] + x2[crossover_point:]
        y2 = x2[:crossover_point] + x1[crossover_point:]
        return y1, y2

    def _uniform_crossover(
        self, x1: List[int], x2: List[int]
    ) -> Tuple[List[int], List[int]]:
        """Perform uniform crossover"""
        n = len(x1)
        y1 = []
        y2 = []

        for i in range(n):
            if random.random() < 0.5:
                y1.append(x1[i])
                y2.append(x2[i])
            else:
                y1.append(x2[i])
                y2.append(x1[i])

        return y1, y2

    def _enforce_capacity_constraints(
        self,
        offspring: List[int],
        picker_capacities: List[int],
        num_pickers: int,
    ) -> List[int]:
        """Ensure solution satisfies picker capacity constraints"""
        assigned_counts = [0] * num_pickers
        for picker_id in offspring:
            assigned_counts[picker_id] += 1

        over_capacity = {
            picker_id: count - picker_capacities[picker_id]
            for picker_id, count in enumerate(assigned_counts)
            if count > picker_capacities[picker_id]
        }

        for i, picker_id in enumerate(offspring):
            if picker_id in over_capacity and over_capacity[picker_id] > 0:
                valid_pickers = [
                    p
                    for p in range(num_pickers)
                    if assigned_counts[p] < picker_capacities[p]
                ]

                if valid_pickers:
                    new_picker = random.choice(valid_pickers)
                    offspring[i] = new_picker
                    assigned_counts[picker_id] -= 1
                    assigned_counts[new_picker] += 1
                    over_capacity[picker_id] -= 1

        return offspring

    def mutate_with_capacity(
        self, x: List[int], picker_capacities: List[int], num_pickers: int
    ) -> List[int]:
        """Mutate solution while respecting capacity constraints"""
        y = x[:]
        attempts = 10

        while attempts > 0:
            j = np.random.randint(len(x))
            assigned_picker = y[j]
            new_picker = np.random.randint(num_pickers)

            y[j] = new_picker

            assigned_counts = [
                y.count(picker_id) for picker_id in range(num_pickers)
            ]
            if all(
                assigned_counts[picker_id] <= picker_capacities[picker_id]
                for picker_id in range(num_pickers)
            ):
                return y

            y[j] = assigned_picker
            attempts -= 1

        return x

    def tournament_selection(
        self, population: List[Tuple[List[int], float]], tournament_size: int
    ) -> List[int]:
        """Select parent using tournament selection"""
        tournament_contestants = random.sample(population, tournament_size)
        winner = sorted(tournament_contestants, key=lambda x: x[1])[0]
        return winner[0]


# For backwards compatibility
def crossover(
    x1: List[int], x2: List[int], picker_capacities: List[int], num_pickers: int
) -> Tuple[List[int], List[int]]:
    """Legacy crossover function"""
    genetic_op = GeneticOperator(RouteOptimizer())
    return genetic_op.crossover(x1, x2, picker_capacities, num_pickers)


def mutate_with_capacity(
    x: List[int], picker_capacities: List[int], num_pickers: int
) -> List[int]:
    """Legacy mutation function"""
    genetic_op = GeneticOperator(RouteOptimizer())
    return genetic_op.mutate_with_capacity(x, picker_capacities, num_pickers)


def tournament_selection(
    population: List[Tuple[List[int], float]], tournament_size: int
) -> List[int]:
    """Legacy tournament selection function"""
    genetic_op = GeneticOperator(RouteOptimizer())
    return genetic_op.tournament_selection(population, tournament_size)
