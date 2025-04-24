"""Ant Colony Optimization implementation for warehouse order picking.

This module provides an implementation of the Ant Colony Optimization algorithm
for solving the order picking problem in a warehouse environment.
"""

import numpy as np
from typing import List, Tuple
from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.utils.config import (
    NUM_PICKERS, ALPHA, BETA, RHO
)

class AntColonyOptimizer:
    """Class for ant colony optimization operations"""
    def __init__(self, route_optimizer: RouteOptimizer):
        self.route_optimizer = route_optimizer

    def calculate_heuristic(
        self,
        orders_assign: List[List[Tuple[float, float]]],
        picker_locations: List[Tuple[float, float]]
    ) -> np.ndarray:
        """Calculate heuristic values for ant colony optimization"""
        heuristic = np.zeros((len(orders_assign), len(picker_locations)))
        for item_idx, item_locs in enumerate(orders_assign):
            for picker_idx, picker_loc in enumerate(picker_locations):
                min_distance = float('inf')
                for loc in item_locs:
                    distance = np.sqrt(
                        (loc[0] - picker_loc[0])**2 +
                        (loc[1] - picker_loc[1])**2
                    )
                    min_distance = min(min_distance, distance)
                heuristic[item_idx][picker_idx] = 1 / (min_distance + 1e-6)
        return heuristic

    def build_solution(
        self,
        pheromone: np.ndarray,
        heuristic: np.ndarray,
        orders_size: int,
        picker_capacities: List[int]
    ) -> List[int]:
        """Build a solution using ACO principles"""
        assignment = [-1] * orders_size
        picker_loads = [0] * NUM_PICKERS
        # Build solution
        for item in range(orders_size):
            valid_pickers = []
            prob = []
            for picker in range(NUM_PICKERS):
                if picker_loads[picker] < picker_capacities[picker]:
                    valid_pickers.append(picker)
                    prob.append(
                        (pheromone[item][picker] ** ALPHA) *
                        (heuristic[item][picker] ** BETA)
                    )
            if valid_pickers:
                prob = np.array(prob)
                prob /= prob.sum()
                chosen_picker = np.random.choice(valid_pickers, p=prob)
                assignment[item] = chosen_picker
                picker_loads[chosen_picker] += 1
        return assignment

    def update_pheromone(
        self,
        pheromone: np.ndarray,
        assignment: List[int],
        fitness_score: float,
        orders_size: int
    ) -> None:
        """Update pheromone trails"""
        for item in range(orders_size):
            if assignment[item] != -1:
                pheromone[item][assignment[item]] *= (1 - RHO)
                pheromone[item][assignment[item]] += 1 / fitness_score

# For backwards compatibility
def calculate_heuristic(
    orders_assign: List[List[Tuple[float, float]]],
    picker_locations: List[Tuple[float, float]]
) -> np.ndarray:
    """Legacy heuristic calculation function"""
    aco = AntColonyOptimizer(RouteOptimizer())
    return aco.calculate_heuristic(orders_assign, picker_locations)
