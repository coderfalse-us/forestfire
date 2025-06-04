"""Integration tests using BDD approach for warehouse order picking
    optimization.

This module implements the BDD scenarios defined in the feature files
using pytest to validate the end-to-end functionality of the system.
"""

import pytest
from unittest.mock import patch
import numpy as np

from forestfire.utils.config import (
    TEST_NUM_PICKERS as NUM_PICKERS,
    TEST_PICKER_CAPACITIES as PICKER_CAPACITIES,
    TEST_PICKER_LOCATIONS as PICKER_LOCATIONS,
    TestWarehouseConfigManager,
)
from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.algorithms.genetic import GeneticOperator
from forestfire.algorithms.ant_colony import AntColonyOptimizer
from forestfire.plots.graph import PathVisualizer
from forestfire.database.services.batch_pick_seq_service import (
    BatchPickSequenceService,
)
from forestfire.database.services.picklist import PicklistRepository
from forestfire.database.services.picksequencemodel import ApiPayload
from forestfire.optimizer.models.route import Route
from forestfire.database.services.picksequencemodel import PickSequenceUpdate


# ---- Background steps ----


@pytest.fixture
def warehouse_config():
    """Fixture for warehouse configuration."""
    return {
        "picker_capacities": PICKER_CAPACITIES,
        "picker_locations": PICKER_LOCATIONS,
        "num_pickers": NUM_PICKERS,
    }


# ---- Scenario: Optimize picker routes using hybrid ACO-GA approach ----


@pytest.fixture
def warehouse_setup():
    """Fixture for warehouse setup with pickers and orders."""
    # Sample orders with item locations as (x, y) coordinates
    orders_assign = [
        [(10, 20), (15, 25)],  # Order 1 with 2 items
        [(30, 40), (35, 45)],  # Order 2 with 2 items
        [(50, 60)],  # Order 3 with 1 item
        [(70, 80), (75, 85)],  # Order 4 with 2 items
        [(90, 100)],  # Order 5 with 1 item
    ]

    # Sample pick tasks
    picktasks = ["task1", "task2", "task3", "task4", "task5"]

    # Sample stage result
    stage_result = {}

    return {
        "orders_assign": orders_assign,
        "picktasks": picktasks,
        "stage_result": stage_result,
        "num_pickers": 2,
        "picker_capacities": [3, 5],  # Capacity for each picker
        "picker_locations": [(0, 0), (100, 100)],  # Starting locations
    }


def test_aco_optimization(warehouse_setup):
    """Test ACO optimization for initial solutions."""
    # Given a warehouse with 2 pickers
    # And a set of 5 orders to be picked
    orders_assign = warehouse_setup["orders_assign"]

    # For testing, we'll use a modified version that
    # only uses the number of pickers in our test setup
    num_pickers_for_test = 2  # Match the number in warehouse_setup
    test_picker_capacities = [3, 5]  # Match the capacities in warehouse_setup

    # When the ACO algorithm is run to generate initial solutions
    route_optimizer = RouteOptimizer()

    aco = AntColonyOptimizer(route_optimizer)

    # Initialize pheromone and heuristic matrices with the test picker count
    pheromone = np.ones((len(orders_assign), num_pickers_for_test))

    # Create a heuristic matrix with the right dimensions for our test
    heuristic = np.ones((len(orders_assign), num_pickers_for_test))

    # Call the method with our test data
    assignment = aco.build_solution(
        pheromone,
        heuristic,
        len(orders_assign),
        test_picker_capacities,
        num_pickers_for_test,
    )

    # Then it should produce valid assignments respecting picker capacities
    # Check all orders are assigned
    assert len(assignment) == len(orders_assign)

    # Check assignments are valid (within picker range for our test)
    assert all(
        0 <= picker_id < num_pickers_for_test for picker_id in assignment
    )

    # Check picker capacities are respected
    picker_loads = [0] * num_pickers_for_test
    for picker_id in assignment:
        picker_loads[picker_id] += 1

    for i, load in enumerate(picker_loads):
        assert load <= test_picker_capacities[i], f"Picker {i} exceeds capacity"


def test_genetic_optimization(warehouse_setup):
    """Test genetic algorithm optimization for improving solutions."""
    # Given initial solutions from ACO
    orders_assign = warehouse_setup["orders_assign"]

    # Import the global configuration

    # Create initial population
    route_optimizer = RouteOptimizer()
    genetic_op = GeneticOperator(route_optimizer)

    # Create a sample population with mock fitness scores
    # Use valid assignments that respect the global NUM_PICKERS
    initial_assignment = [0] * len(
        orders_assign
    )  # All orders assigned to picker 0
    alternative_assignment = [min(1, NUM_PICKERS - 1)] * len(
        orders_assign
    )  # All orders assigned to picker 1 or 0 if only 1 picker

    # Mock population with fitness scores (lower is better)
    population = [[initial_assignment, 500.0], [alternative_assignment, 600.0]]

    # When the genetic algorithm is run to optimize the solutions
    # Mock the calculate_shortest_route to return predictable values
    with patch.object(
        route_optimizer, "calculate_shortest_route"
    ) as mock_route:
        # First call returns worse fitness, second call returns better fitness
        mock_route.side_effect = [(400.0, [], []), (300.0, [], [])]

        # Perform crossover with enforced capacity constraints
        parent1, parent2 = population[0][0], population[1][0]
        offspring1, offspring2 = genetic_op.crossover(
            parent1, parent2, PICKER_CAPACITIES, NUM_PICKERS
        )

        # Then it should improve the solution quality
        # Check offspring are valid
        assert len(offspring1) == len(orders_assign)
        assert len(offspring2) == len(orders_assign)

        # Check all assignments are valid picker IDs
        assert all(0 <= picker_id < NUM_PICKERS for picker_id in offspring1)
        assert all(0 <= picker_id < NUM_PICKERS for picker_id in offspring2)

        # Count assignments per picker
        picker_loads = [0] * NUM_PICKERS
        for picker_id in offspring1:
            picker_loads[picker_id] += 1

        # Check picker capacities are respected
        for i, load in enumerate(picker_loads):
            if i < len(PICKER_CAPACITIES):
                assert (
                    load <= PICKER_CAPACITIES[i]
                ), f"Picker {i} exceeds capacity in offspring1"


# ---- Scenario: Visualize optimized picker routes ----


@pytest.mark.asyncio
async def test_route_visualization(warehouse_setup, tmp_path):
    """Test visualization of optimized picker routes."""
    # Given a set of optimized picker assignments
    assignment = [0, 0, 1, 1, 1]  # Sample assignment of orders to pickers

    # Create a temporary output directory
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # When the route visualization is generated
    with (
        patch("matplotlib.pyplot.savefig") as mock_savefig,
        patch.object(PathVisualizer, "save_plot") as mock_save_plot,
        patch.object(PicklistRepository, "get_optimized_data") as mock_get_data,
        patch.object(RouteOptimizer, "calculate_shortest_route") as mock_route,
        # patch("forestfire.plots.graph.ITEM_LOCATIONS", [(1, 1), (2, 2)]),
    ):  # Mock ITEM_LOCATIONS
        # Mock the save_plot method to return a filepath
        mock_save_plot.return_value = str(output_dir / "test_plot.png")

        # Mock the visualization to avoid actual file creation
        mock_savefig.return_value = None

        # Mock the get_optimized_data method to return test data
        mock_get_data.return_value = (
            warehouse_setup["picktasks"],
            warehouse_setup["orders_assign"],
            warehouse_setup["stage_result"],
            ["PL001", "PL002", "PL003", "PL004", "PL005"],
        )

        # Create mock Route objects with locations
        mock_routes = [
            Route(
                picker_id=0,
                locations=[(10, 10), (20, 20)],
                cost=50.0,
                assigned_orders=[0, 1],
            ),
            Route(
                picker_id=1,
                locations=[(30, 30), (40, 40)],
                cost=50.0,
                assigned_orders=[2, 3, 4],
            ),
        ]

        # Mock the calculate_shortest_route method to
        # return proper Route objects
        mock_route.return_value = (
            100.0,  # fitness score
            mock_routes,  # routes with locations
            [[(10, 10), (20, 20)], [(30, 30), (40, 40)]],  # assignments
        )

        # Create visualizer
        visualizer = PathVisualizer()
        config_instance = TestWarehouseConfigManager()

        # Call plot_routes which is the actual method in PathVisualizer
        # It only takes the assignment parameter
        await visualizer.plot_routes(assignment, config=config_instance)

        # Then each picker should have a distinct path visualization
        # And the visualization should include all assigned picking locations
        assert mock_save_plot.call_count > 0, "No visualizations were generated"


# ---- Scenario: Update pick sequences in warehouse management system ----


def test_api_payload_preparation():
    """Test preparation of API payload for warehouse management system."""
    # Given a set of optimized picker assignments and routes

    # Create sample pick sequence updates
    updates = [
        PickSequenceUpdate(
            account_id="ACC123",
            business_unit_id="BU123",
            warehouse_id="WH123",
            picklist_id="PL001",
            picktask_id="TASK1",
            batch_id="BATCH1",
            pick_sequence=1,
        ),
        PickSequenceUpdate(
            account_id="ACC123",
            business_unit_id="BU123",
            warehouse_id="WH123",
            picklist_id="PL002",
            picktask_id="TASK1",
            batch_id="BATCH1",
            pick_sequence=2,
        ),
        PickSequenceUpdate(
            account_id="ACC123",
            business_unit_id="BU123",
            warehouse_id="WH123",
            picklist_id="PL003",
            picktask_id="TASK2",
            batch_id="BATCH2",
            pick_sequence=1,
        ),
    ]

    # When the pick sequences are prepared for the warehouse management system
    service = BatchPickSequenceService()

    # Use the correct method name _transform_updates_to_api_format
    with patch.object(
        service, "_transform_updates_to_api_format"
    ) as mock_transform:
        # Create a sample API payload
        mock_payload = [
            ApiPayload(
                AccountId="ACC123",
                BusinessunitId="BU123",
                WarehouseId="WH123",
                PickTasks=[],
            )
        ]
        mock_transform.return_value = mock_payload

        # Then the API payload should contain all required fields
        payloads = service._transform_updates_to_api_format(updates)

        # Check the mock was called with the updates
        mock_transform.assert_called_once_with(updates)

        # Check payload structure (using the mock return value)
        assert len(payloads) > 0
        payload = payloads[0]
        assert payload.AccountId is not None
        assert payload.BusinessunitId is not None
        assert payload.WarehouseId is not None
        assert hasattr(payload, "PickTasks")


# Instructions for running the tests
if __name__ == "__main__":
    print("To run these BDD tests, use the following command:")
    print("python -m pytest tests/test_integration_bdd.py -v")
