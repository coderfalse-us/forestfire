"""Test configuration for the forestfire project.

This module provides fixtures and configuration for pytest.
"""

import pytest
import numpy as np
from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.algorithms.genetic import GeneticOperator
from forestfire.algorithms.ant_colony import AntColonyOptimizer
from forestfire.plots.graph import PathVisualizer
from forestfire.utils.config import NUM_PICKERS

@pytest.fixture
def route_optimizer():
    """Fixture for RouteOptimizer instance."""
    return RouteOptimizer()

@pytest.fixture
def genetic_operator(route_optimizer):
    """Fixture for GeneticOperator instance."""
    # pylint: disable=redefined-outer-name
    return GeneticOperator(route_optimizer)

@pytest.fixture
def ant_colony_optimizer(route_optimizer):
    """Fixture for AntColonyOptimizer instance."""
    # pylint: disable=redefined-outer-name
    return AntColonyOptimizer(route_optimizer)

@pytest.fixture
def path_visualizer():
    """Fixture for PathVisualizer instance."""
    return PathVisualizer()

@pytest.fixture
def sample_orders_assign():
    """Fixture for sample orders assignment data."""
    return [
        [(10, 20), (15, 25)],
        [(30, 40), (35, 45)],
        [(50, 60), (55, 65)],
        [(70, 80), (75, 85)],
        [(90, 100), (95, 105)]
    ]

@pytest.fixture
def sample_picktasks():
    """Fixture for sample picktasks data."""
    return ["task1", "task2", "task3", "task4", "task5"]

@pytest.fixture
def sample_stage_result():
    """Fixture for sample staging area result data."""
    return {
        "task1": [(5, 5)],
        "task2": [(15, 15)],
        "task3": [(25, 25)],
        "task4": [(35, 35)],
        "task5": [(45, 45)]
    }

@pytest.fixture
def sample_assignment():
    """Fixture for sample picker assignment."""
    return [0, 1, 2, 0, 1]

@pytest.fixture
def sample_population():
    """Fixture for sample population with fitness scores."""
    return [
        [[0, 1, 2, 0, 1], 100.0],
        [[1, 0, 2, 1, 0], 120.0],
        [[2, 1, 0, 2, 1], 150.0],
        [[0, 2, 1, 0, 2], 110.0],
        [[1, 2, 0, 1, 2], 130.0]
    ]

@pytest.fixture
def sample_pheromone():
    """Fixture for sample pheromone matrix."""
    return np.ones((5, NUM_PICKERS))

@pytest.fixture
def sample_heuristic():
    """Fixture for sample heuristic matrix."""
    return np.array([
        [0.1, 0.2, 0.3, 0.4, 0.5, 0.1, 0.2, 0.3, 0.4, 0.5],
        [0.5, 0.4, 0.3, 0.2, 0.1, 0.5, 0.4, 0.3, 0.2, 0.1],
        [0.2, 0.3, 0.4, 0.5, 0.1, 0.2, 0.3, 0.4, 0.5, 0.1],
        [0.3, 0.4, 0.5, 0.1, 0.2, 0.3, 0.4, 0.5, 0.1, 0.2],
        [0.4, 0.5, 0.1, 0.2, 0.3, 0.4, 0.5, 0.1, 0.2, 0.3]
    ])
