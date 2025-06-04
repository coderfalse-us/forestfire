"""Tests for the warehouse optimizer module."""

import pytest
from unittest.mock import patch, MagicMock
from forestfire.core.optimizer import WarehouseOptimizer
from forestfire.utils.config import WarehouseConfigManager, WarehouseConfig

# pylint: disable=redefined-outer-name


@pytest.fixture
def test_warehouse_config():
    """Create test warehouse configuration."""
    return WarehouseConfig(
        num_pickers=2,
        picker_capacities=[3, 3],
        picker_locations=[(0, 0), (10, 10)],
        warehouse_name="TEST",
    )


@pytest.fixture
def optimizer():
    """Create WarehouseOptimizer instance with test configuration."""
    optimizer = WarehouseOptimizer()
    return optimizer


class TestWarehouseOptimizer:
    """Test cases for the WarehouseOptimizer class."""

    def test_initialize_population(self, optimizer, test_warehouse_config):
        """Test population initialization."""
        num_orders = 5
        population = optimizer.initialize_population(
            test_warehouse_config.num_pickers,
            num_orders,
            test_warehouse_config.picker_capacities,
        )

        assert len(population) == optimizer.n_pop - 1
        for assignment in population:
            assert len(assignment) == num_orders
            # Verify capacity constraints
            picker_loads = [
                assignment.count(i)
                for i in range(test_warehouse_config.num_pickers)
            ]
            assert all(
                load <= cap
                for load, cap in zip(
                    picker_loads, test_warehouse_config.picker_capacities
                )
            )

    def test_run_aco_optimization(self, optimizer, test_warehouse_config):
        """Test ACO optimization phase."""
        orders_assign = [[(1, 1)], [(2, 2)], [(3, 3)]]
        picktasks = ["task1", "task2", "task3"]
        stage_result = {"task1": [(1, 1)]}

        # Mock route optimizer
        optimizer.route_optimizer.calculate_shortest_route = MagicMock(
            return_value=(100.0, [], [])
        )

        solutions = optimizer.run_aco_optimization(
            optimizer.ant_colony_optimizer,
            optimizer.route_optimizer,
            orders_assign,
            picktasks,
            stage_result,
            test_warehouse_config.picker_locations,
            test_warehouse_config.num_pickers,
            test_warehouse_config.picker_capacities,
        )

        assert len(solutions) > 0
        assert all(
            len(solution) == 2 for solution in solutions
        )  # [assignment, fitness]
        assert all(isinstance(solution[1], float) for solution in solutions)

    def test_run_genetic_optimization(self, optimizer, test_warehouse_config):
        """Test genetic optimization phase."""
        # Create a larger initial population
        initial_pop = [
            ([0, 1, 0], 200.0) for _ in range(10)
        ]  # Increased population size
        orders_assign = [[(1, 1)], [(2, 2)], [(3, 3)]]
        picktasks = ["task1", "task2", "task3"]
        stage_result = {"task1": [(1, 1)]}

        # Mock route optimizer
        optimizer.route_optimizer.calculate_shortest_route = MagicMock(
            return_value=(100.0, [], [])
        )

        solution = optimizer.run_genetic_optimization(
            optimizer.genetic_operator,
            optimizer.route_optimizer,
            initial_pop,
            orders_assign,
            picktasks,
            stage_result,
            test_warehouse_config.picker_locations,
            test_warehouse_config.picker_capacities,
            test_warehouse_config.num_pickers,
        )

        assert isinstance(solution, list)
        assert len(solution) == len(orders_assign)
        assert all(0 <= x < test_warehouse_config.num_pickers for x in solution)

    @pytest.mark.asyncio
    async def test_optimize_main(self, optimizer, test_warehouse_config):
        """Test main optimization workflow."""
        # Create config manager with proper attribute access
        config_manager = WarehouseConfigManager(test_warehouse_config)
        config_manager.NUM_PICKERS = test_warehouse_config.num_pickers
        config_manager.PICKER_CAPACITIES = (
            test_warehouse_config.picker_capacities
        )
        config_manager.PICKER_LOCATIONS = test_warehouse_config.picker_locations
        config_manager.WAREHOUSE_NAME = test_warehouse_config.warehouse_name

        with patch.object(
            optimizer.picklist_repository, "get_optimized_data"
        ) as mock_get_data:
            # Mock data
            mock_get_data.return_value = (
                ["task1", "task2"],  # picktasks
                [[(1, 1)], [(2, 2)]],  # orders_assign
                {"task1": [(1, 1)]},  # stage_result
                ["id1", "id2"],  # picklistids
            )

            # Execute with config_manager instead of test_warehouse_config
            result = await optimizer.optimize_main(config_manager)

            # Verify
            assert result is not None
            mock_get_data.assert_called_once_with(
                test_warehouse_config.warehouse_name
            )
