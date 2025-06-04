"""
Module for optimizing warehouse operations using
genetic algorithms and ant colony optimization
"""

from loguru import logger
from typing import List, Any, Tuple
import random

import numpy as np

from forestfire.utils.config import (
    N_POP,
    NUM_ANTS,
    MAX_IT,
    NC,
    NM,
    TOURNAMENT_SIZE,
    STEP_BETWEEN_ROWS,
    LEFT_WALKWAY,
    RIGHT_WALKWAY,
    ROWS,
    COLS,
    WarehouseConfigManager,
)
from forestfire.database.services.picklist import PicklistRepository
from forestfire.database.services.batch_pick_seq_service import (
    BatchPickSequenceService,
)
from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.algorithms.genetic import GeneticOperator
from forestfire.algorithms.ant_colony import AntColonyOptimizer
from forestfire.plots.graph import PathVisualizer


class WarehouseOptimizer:
    """Class for optimizing warehouse operations"""

    def __init__(self):
        self.max_it = MAX_IT
        self.n_pop = N_POP
        self.num_ants = NUM_ANTS
        self.nc = NC
        self.nm = NM
        self.tournament_size = TOURNAMENT_SIZE
        self.step_between_rows = STEP_BETWEEN_ROWS
        self.left_walkway = LEFT_WALKWAY
        self.right_walkway = RIGHT_WALKWAY
        self.rows = ROWS
        self.cols = COLS
        self.picklist_repository = PicklistRepository()
        self.batch_pick_sequence_service = BatchPickSequenceService()
        self.route_optimizer = RouteOptimizer()
        self.genetic_operator = GeneticOperator(self.route_optimizer)
        self.ant_colony_optimizer = AntColonyOptimizer(self.route_optimizer)
        self.path_visualizer = PathVisualizer()

    def initialize_population(
        self, num_pickers: int, orders_size: int, picker_capacities: List[int]
    ) -> List[List[int]]:
        """Initialize population with valid picker assignments.

        Args:
            num_pickers: Number of available pickers
            orders_size: Number of orders to assign
            picker_capacities: List of picker capacity constraints

        Returns:
            List of valid picker assignments
        """
        population = []
        for _ in range(self.n_pop - 1):
            assignment = []
            assigned_counts = [0] * num_pickers
            for _ in range(orders_size):
                valid_pickers = [
                    i
                    for i in range(num_pickers)
                    if assigned_counts[i] < picker_capacities[i]
                ]
                picker_id = random.choice(valid_pickers)
                assigned_counts[picker_id] += 1
                assignment.append(picker_id)
            random.shuffle(assignment)
            population.append(assignment)
        return population

    def run_aco_optimization(
        self,
        aco: AntColonyOptimizer,
        route_optimizer: RouteOptimizer,
        orders_assign: List[Any],
        picktasks: List[Any],
        stage_result: Any,
        picker_location: Tuple[float, float],
        num_pickers: int,
        picker_capacities: List[int],
    ) -> List[List[Any]]:
        """Run Ant Colony Optimization phase.

        Args:
            aco: Ant Colony Optimizer instance
            route_optimizer: Route Optimizer instance
            orders_assign: List of orders to assign
            picktasks: List of picking tasks
            stage_result: Staging area result data

            Returns:
                List of solutions with their fitness scores
        """
        empty_pop = []
        pheromone = np.ones((len(orders_assign), num_pickers))
        heuristic = aco.calculate_heuristic(orders_assign, picker_location)
        for _ in range(self.num_ants):
            assignment = aco.build_solution(
                pheromone,
                heuristic,
                len(orders_assign),
                picker_capacities,
                num_pickers,
            )
            fitness_score, _, _ = route_optimizer.calculate_shortest_route(
                num_pickers,
                picker_location,
                assignment,
                orders_assign,
                picktasks,
                stage_result,
            )
            empty_pop.append([assignment, fitness_score])
            aco.update_pheromone(
                pheromone, assignment, fitness_score, len(orders_assign)
            )
        return empty_pop

    def run_genetic_optimization(
        self,
        genetic_op: GeneticOperator,
        route_optimizer: RouteOptimizer,
        pop: List[List[Any]],
        orders_assign: List[Any],
        picktasks: List[Any],
        stage_result: Any,
        picker_location: Tuple[float, float],
        picker_capacities: List[int],
        num_pickers: int,
    ) -> List[int]:
        """Run Genetic Algorithm optimization phase.

        Args:
            genetic_op: Genetic Operator instance
            route_optimizer: Route Optimizer instance
            pop: Initial population
            orders_assign: List of orders to assign
            picktasks: List of picking tasks
            stage_result: Staging area result data

            Returns:
                Best solution found
        """
        for iteration in range(self.max_it):
            crossover_population = []
            for _ in range(self.nc // 2):
                parent1 = genetic_op.tournament_selection(
                    pop, self.tournament_size
                )
                parent2 = genetic_op.tournament_selection(
                    pop, self.tournament_size
                )
                offspring1, offspring2 = genetic_op.crossover(
                    parent1,
                    parent2,
                    picker_capacities,
                    num_pickers,
                )
                fitness1, _, _ = route_optimizer.calculate_shortest_route(
                    num_pickers,
                    picker_location,
                    offspring1,
                    orders_assign,
                    picktasks,
                    stage_result,
                )
                fitness2, _, _ = route_optimizer.calculate_shortest_route(
                    num_pickers,
                    picker_location,
                    offspring2,
                    orders_assign,
                    picktasks,
                    stage_result,
                )
                crossover_population.extend(
                    [[offspring1, fitness1], [offspring2, fitness2]]
                )

            mutation_population = []
            for _ in range(self.nm):
                parent = random.choice(pop)[0]
                offspring = genetic_op.mutate_with_capacity(
                    parent, picker_capacities, num_pickers
                )
                fitness, _, _ = route_optimizer.calculate_shortest_route(
                    num_pickers,
                    picker_location,
                    offspring,
                    orders_assign,
                    picktasks,
                    stage_result,
                )
                mutation_population.append([offspring, fitness])

            pop.extend(crossover_population + mutation_population)
            pop.sort(key=lambda x: x[1])
            pop = pop[: self.n_pop]
            logger.info(
                "Iteration {}: Best Solution = {:.6f}", iteration, pop[0][1]
            )
        return pop[0][0]

    async def optimize_main(self, config: WarehouseConfigManager) -> None:
        """Main method to run the optimization process."""
        num_pickers = config.NUM_PICKERS
        picker_capacities = config.PICKER_CAPACITIES
        picker_locations = config.PICKER_LOCATIONS
        warehouse_name = config.WAREHOUSE_NAME

        logger.info(
            "Starting optimization with {} pickers", num_pickers, color="cyan"
        )

        # Fetch data from the database
        (
            picktasks,
            orders_assign,
            stage_result,
            picklistids,
        ) = await self.picklist_repository.get_optimized_data(warehouse_name)

        # Initialize population
        initial_population = self.initialize_population(
            num_pickers, len(orders_assign), picker_capacities
        )

        empty_pop = []
        for position in initial_population:
            fitness_score, _, _ = self.route_optimizer.calculate_shortest_route(
                num_pickers,
                picker_locations,
                position,
                orders_assign,
                picktasks,
                stage_result,
            )
            empty_pop.append([position, fitness_score])

        # Run Ant Colony Optimization
        aco_solutions = self.run_aco_optimization(
            self.ant_colony_optimizer,
            self.route_optimizer,
            orders_assign,
            picktasks,
            stage_result,
            picker_locations,
            num_pickers,
            picker_capacities,
        )
        empty_pop.extend(aco_solutions)

        # Run Genetic Algorithm Optimization
        pop = sorted(empty_pop, key=lambda x: x[1])
        final_solution = self.run_genetic_optimization(
            self.genetic_operator,
            self.route_optimizer,
            pop,
            orders_assign,
            picktasks,
            stage_result,
            picker_locations,
            picker_capacities,
            num_pickers,
        )
        logger.info("\nFinal Best Solution: {}", final_solution)

        # Visualize the best solution
        await self.path_visualizer.plot_routes(final_solution, config)
        await self.batch_pick_sequence_service.update_pick_sequences(
            num_pickers,
            picker_locations,
            final_solution,
            picklistids,
            orders_assign,
            picktasks,
            stage_result,
        )

        return final_solution


# uvicorn forestfire.api.app:app --reload
