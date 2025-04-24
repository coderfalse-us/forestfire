"""Main module for warehouse order picking
   optimization using hybrid ACO-GA approach."""

import logging
from typing import List, Any
import random

import numpy as np

from forestfire.utils.config import (
    NUM_PICKERS, PICKER_CAPACITIES, PICKER_LOCATIONS,
    N_POP, NUM_ANTS, MAX_IT, NC, NM, TOURNAMENT_SIZE
)
from forestfire.database.services.picklist import PicklistRepository
from forestfire.database.services.batch_pick_seq_service import BatchPickSequenceService
from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.algorithms.genetic import GeneticOperator
from forestfire.algorithms.ant_colony import AntColonyOptimizer
from forestfire.plots.graph import PathVisualizer


logger = logging.getLogger(__name__)


def initialize_population(
    num_pickers: int,
    orders_size: int,
    picker_capacities: List[int]
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
    for _ in range(N_POP - 1):
        assignment = []
        assigned_counts = [0] * num_pickers
        for _ in range(orders_size):
            valid_pickers = [
                i for i in range(num_pickers)
                if assigned_counts[i] < picker_capacities[i]
            ]
            picker_id = random.choice(valid_pickers)
            assigned_counts[picker_id] += 1
            assignment.append(picker_id)
        random.shuffle(assignment)
        population.append(assignment)
    return population


def run_aco_optimization(
    aco: AntColonyOptimizer,
    route_optimizer: RouteOptimizer,
    orders_assign: List[Any],
    picktasks: List[Any],
    stage_result: Any
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
    pheromone = np.ones((len(orders_assign), NUM_PICKERS))
    heuristic = aco.calculate_heuristic(orders_assign, PICKER_LOCATIONS)
    for _ in range(NUM_ANTS):
        assignment = aco.build_solution(
            pheromone, heuristic, len(orders_assign), PICKER_CAPACITIES
        )
        fitness_score, _, _ = route_optimizer.calculate_shortest_route(
            PICKER_LOCATIONS,
            assignment,
            orders_assign,
            picktasks,
            stage_result
        )
        empty_pop.append([assignment, fitness_score])
        aco.update_pheromone(pheromone,
                            assignment,
                            fitness_score,
                            len(orders_assign))
    return empty_pop


def run_genetic_optimization(
    genetic_op: GeneticOperator,
    route_optimizer: RouteOptimizer,
    pop: List[List[Any]],
    orders_assign: List[Any],
    picktasks: List[Any],
    stage_result: Any
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
    for iteration in range(MAX_IT):
        crossover_population = []
        for _ in range(NC // 2):
            parent1 = genetic_op.tournament_selection(pop, TOURNAMENT_SIZE)
            parent2 = genetic_op.tournament_selection(pop, TOURNAMENT_SIZE)
            offspring1, offspring2 = genetic_op.crossover(parent1, parent2)
            fitness1, _, _ = route_optimizer.calculate_shortest_route(
                PICKER_LOCATIONS,
                offspring1,
                orders_assign,
                picktasks,
                stage_result
            )
            fitness2, _, _ = route_optimizer.calculate_shortest_route(
                PICKER_LOCATIONS,
                offspring2,
                orders_assign,
                picktasks,
                stage_result
            )
            crossover_population.extend([[offspring1, fitness1],
                                        [offspring2, fitness2]])

        mutation_population = []
        for _ in range(NM):
            parent = random.choice(pop)[0]
            offspring = genetic_op.mutate_with_capacity(
                        parent,
                        PICKER_CAPACITIES
                        )
            fitness, _, _ = route_optimizer.calculate_shortest_route(
                PICKER_LOCATIONS,
                offspring,
                orders_assign,
                picktasks,
                stage_result
            )
            mutation_population.append([offspring, fitness])

        pop.extend(crossover_population + mutation_population)
        pop.sort(key=lambda x: x[1])
        pop = pop[:N_POP]
        logger.info('Iteration %d: Best Solution = %f', iteration, pop[0][1])
    return pop[0][0]


def main() -> None:
    """Main execution function."""
    services = {
        'picklist_repo': PicklistRepository(),
        'route_optimizer': RouteOptimizer(),
        'genetic_op': GeneticOperator(RouteOptimizer()),
        'aco': AntColonyOptimizer(RouteOptimizer()),
        'path_visualizer': PathVisualizer(),
        'picksequence_service': BatchPickSequenceService()
    }

    # Get optimization data
    picktasks, orders_assign, stage_result, picklistids = (
        services['picklist_repo'].get_optimized_data()
    )

    # Initialize and evaluate population
    initial_population = initialize_population(
        NUM_PICKERS, len(orders_assign), PICKER_CAPACITIES
    )
    empty_pop = []
    for position in initial_population:
        route_optimizer = services['route_optimizer']
        fitness_score, _, _ = route_optimizer.calculate_shortest_route(
            PICKER_LOCATIONS,
            position,
            orders_assign,
            picktasks,
            stage_result
        )
        empty_pop.append([position, fitness_score])

    # Run ACO optimization
    aco_solutions = run_aco_optimization(
        services['aco'], services['route_optimizer'],
        orders_assign, picktasks, stage_result
    )
    empty_pop.extend(aco_solutions)

    # Run GA optimization
    pop = sorted(empty_pop, key=lambda x: x[1])
    final_solution = run_genetic_optimization(
        services['genetic_op'], services['route_optimizer'],
        pop, orders_assign, picktasks, stage_result
    )
    logger.info('\nFinal Best Solution: %s', final_solution)

    # Visualize and update results
    services['path_visualizer'].plot_routes(final_solution)
    services['picksequence_service'].update_pick_sequences(
        final_solution, picklistids, orders_assign, picktasks, stage_result
    )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        main()
    except Exception as e:
        logger.error('Error in optimization process: %s', e)
        raise
