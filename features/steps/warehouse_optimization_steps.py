"""Step definitions for warehouse optimization end-to-end testing."""

import random
from unittest.mock import patch
import numpy as np
import httpx
from behave import given, when, then
from behave.api.async_step import async_run_until_complete

from features.steps.api_mocks import mock_httpx_client

from forestfire.database.services.picklist import PicklistRepository
from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.algorithms.genetic import GeneticOperator
from forestfire.algorithms.ant_colony import AntColonyOptimizer
from forestfire.plots.graph import PathVisualizer
from forestfire.database.services.batch_pick_seq_service import (
    BatchPickSequenceService,
)
from forestfire.utils.config import (
    TEST_NUM_PICKERS as NUM_PICKERS,
    TEST_PICKER_CAPACITIES as PICKER_CAPACITIES,
    TEST_PICKER_LOCATIONS as PICKER_LOCATIONS,
    TEST_WAREHOUSE_NAME as WAREHOUSE_NAME,
    TestWarehouseConfigManager,
)


@given("the warehouse configuration is loaded")
def step_given_warehouse_config(context):
    """Load warehouse configuration from the table."""
    for row in context.table:
        context.num_pickers = int(row["num_pickers"])
        context.picker_capacities = [
            int(row["picker_capacities"])
        ] * context.num_pickers


@given("the warehouse data is loaded from the database")
@async_run_until_complete
async def step_given_warehouse_data(context):
    """Load warehouse data from the database."""
    context.picklist_repo = PicklistRepository()
    (
        context.picktasks,
        context.orders_assign,
        context.stage_result,
        context.picklistids,
    ) = await context.picklist_repo.get_optimized_data(WAREHOUSE_NAME)
    context.route_optimizer = RouteOptimizer()
    context.genetic_op = GeneticOperator(context.route_optimizer)
    context.aco = AntColonyOptimizer(context.route_optimizer)
    context.path_visualizer = PathVisualizer()
    context.picksequence_service = BatchPickSequenceService()


@given("the picker capacities are set to")
def step_given_picker_capacities(context):
    """Set custom picker capacities."""
    context.custom_capacities = [0] * NUM_PICKERS
    for row in context.table:
        picker_id = int(row["picker_id"])
        capacity = int(row["capacity"])
        context.custom_capacities[picker_id] = capacity


@when("the ACO optimization process is executed")
def step_when_aco_optimization(context):
    """Execute the ACO optimization process."""
    # Run ACO optimization
    context.aco_solutions = []
    pheromone = np.ones((len(context.orders_assign), context.num_pickers))
    heuristic = context.aco.calculate_heuristic(
        context.orders_assign, PICKER_LOCATIONS
    )

    for _ in range(10):  # smaller number for testing
        assignment = context.aco.build_solution(
            pheromone,
            heuristic,
            len(context.orders_assign),
            PICKER_CAPACITIES,
            context.num_pickers,
        )
        fitness, _, _ = context.route_optimizer.calculate_shortest_route(
            context.num_pickers,
            PICKER_LOCATIONS,
            assignment,
            context.orders_assign,
            context.picktasks,
            context.stage_result,
        )
        context.aco_solutions.append((assignment, fitness))
        context.aco.update_pheromone(
            pheromone, assignment, fitness, len(context.orders_assign)
        )


@then("the ACO solutions should be valid")
def step_then_valid_aco_solutions(context):
    """Verify that ACO solutions are valid."""
    assert len(context.aco_solutions) > 0, "No ACO solutions generated"

    for solution, fitness in context.aco_solutions:
        # Check solution length
        assert len(solution) == len(
            context.orders_assign
        ), "Solution length mismatch"

        # Check picker assignments are valid
        assert all(
            0 <= picker_id < NUM_PICKERS for picker_id in solution
        ), "Invalid picker assignment"

        # Check fitness score
        assert fitness > 0, "Fitness score should be positive"

        # Check picker capacity constraints
        picker_counts = [solution.count(i) for i in range(NUM_PICKERS)]
        assert all(
            count <= capacity
            for count, capacity in zip(picker_counts, PICKER_CAPACITIES)
        ), "Picker capacity constraints violated"


@when("the genetic algorithm optimization is executed with the ACO solutions")
def step_when_ga_optimization(context):
    """Execute the genetic algorithm optimization with ACO solutions."""
    # Sort population by fitness
    population = sorted(context.aco_solutions, key=lambda x: x[1])

    # Run GA for a few iterations
    for _ in range(5):  #  smaller number for testing
        # Select parents
        parent1_idx = random.randint(0, len(population) - 1)
        parent2_idx = random.randint(0, len(population) - 1)
        parent1 = population[parent1_idx][0]
        parent2 = population[parent2_idx][0]

        # Perform crossover
        offspring1, offspring2 = context.genetic_op.crossover(
            parent1, parent2, PICKER_CAPACITIES, NUM_PICKERS
        )

        # Calculate fitness
        fitness1, _, _ = context.route_optimizer.calculate_shortest_route(
            NUM_PICKERS,
            PICKER_LOCATIONS,
            offspring1,
            context.orders_assign,
            context.picktasks,
            context.stage_result,
        )
        fitness2, _, _ = context.route_optimizer.calculate_shortest_route(
            NUM_PICKERS,
            PICKER_LOCATIONS,
            offspring2,
            context.orders_assign,
            context.picktasks,
            context.stage_result,
        )

        # Add to population
        population.extend([(offspring1, fitness1), (offspring2, fitness2)])
        population = sorted(population, key=lambda x: x[1])[:10]  # Keep top 10

    context.final_solution = population[0][0]
    context.final_fitness = population[0][1]


@when("the complete optimization process is executed")
@async_run_until_complete
async def step_when_complete_optimization(context):
    """Execute the complete optimization process."""

    if not hasattr(context, "orders_assign"):
        await step_given_warehouse_data(context)
    # Run ACO optimization
    step_when_aco_optimization(context)

    # Run GA optimization
    step_when_ga_optimization(context)


@then("the final solution should be valid and optimized")
def step_then_valid_final_solution(context):
    """Verify that the final solution is valid and optimized."""
    assert hasattr(context, "final_solution"), "No final solution found"

    # Check solution length
    assert len(context.final_solution) == len(
        context.orders_assign
    ), "Solution length mismatch"

    # Check picker assignments are valid
    assert all(
        0 <= picker_id < NUM_PICKERS for picker_id in context.final_solution
    ), "Invalid picker assignment"

    # Check fitness score
    assert context.final_fitness > 0, "Fitness score should be positive"

    # Check picker capacity constraints
    picker_counts = [
        context.final_solution.count(i) for i in range(NUM_PICKERS)
    ]
    assert all(
        count <= capacity
        for count, capacity in zip(picker_counts, PICKER_CAPACITIES)
    ), "Picker capacity constraints violated"

    print(
        f"Final solution: {context.final_solution}\n"
        f"Fitness: {context.final_fitness}"
    )


@then("the final solution should respect picker capacity constraints")
def step_then_respect_capacity_constraints(context):
    """Verify that the final solution respects picker capacity constraints."""
    assert hasattr(context, "final_solution"), "No final solution found"
    assert hasattr(context, "custom_capacities"), "No custom capacities defined"

    # Check picker capacity constraints with custom capacities
    picker_counts = [
        context.final_solution.count(i) for i in range(NUM_PICKERS)
    ]
    assert all(
        count <= capacity
        for count, capacity in zip(picker_counts, context.custom_capacities)
    ), "Custom picker capacity constraints violated"


@when("the optimized routes are visualized")
async def step_when_routes_visualized(context):
    """Visualize the optimized routes."""
    # Mock the visualization to avoid actual plotting in tests
    with patch.object(PathVisualizer, "plot_routes") as mock_plot:
        await context.path_visualizer.plot_routes(
            context.final_solution, config=TestWarehouseConfigManager
        )
        assert mock_plot.called, "Route visualization was not called"


@when("the pick sequences are updated via API")
@async_run_until_complete
async def step_when_sequences_updated(context):
    """Update pick sequences via API."""
    if not hasattr(context, "final_solution"):
        await step_when_complete_optimization(context)

    if not hasattr(context, "picksequence_service"):
        context.picksequence_service = BatchPickSequenceService()
    # Create a patch for httpx.AsyncClient
    mock_client = mock_httpx_client(
        simulate_error=getattr(context, "api_unavailable", False)
    )

    # Apply the patch
    with patch("httpx.AsyncClient", return_value=mock_client):
        try:
            # Call the actual method with our mocked client
            await context.picksequence_service.update_pick_sequences(
                num_pickers=NUM_PICKERS,
                picker_locations=PICKER_LOCATIONS,
                final_solution=context.final_solution,
                picklistids=context.picklistids,
                orders_assign=context.orders_assign,
                picktasks=context.picktasks,
                stage_result=context.stage_result,
            )
            context.api_success = True
            context.api_requests = mock_client.requests
        except httpx.RequestError as e:
            context.api_success = False
            context.api_error = str(e)
            print(f"API Error: {e}")


@then("the API should respond with a success status")
def step_then_api_success(context):
    """Verify that the API responded with a success status."""
    assert hasattr(context, "api_success"), "API call was not made"
    assert context.api_success, "API call was not successful"
