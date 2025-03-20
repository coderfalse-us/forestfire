from forestfire.utils.config import *
from forestfire.database.picklist import PicklistRepository
from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.algorithms.genetic import GeneticOperator
#from forestfire.plots.graph import graph_plot
from typing import List, Tuple
import random
import numpy as np
import math
import logging

logger = logging.getLogger(__name__)

def initialize_population(num_pickers: int, orders_size: int, picker_capacities: List[int]) -> List:
    """Initialize population with valid picker assignments"""
    population = []
    
    for _ in range(N_POP - 1):  # Changed from hardcoded 25-1 to N_POP-1
        assignment = []
        assigned_counts = [0] * num_pickers
        
        for _ in range(orders_size):
            valid_pickers = [i for i in range(num_pickers) 
                           if assigned_counts[i] < picker_capacities[i]]
            picker_id = random.choice(valid_pickers)
            assigned_counts[picker_id] += 1
            assignment.append(picker_id)
            
        random.shuffle(assignment)
        population.append(assignment)
        
    return population

def calculate_heuristic(
    orders_assign: List[List[Tuple[float, float]]], 
    picker_locations: List[Tuple[float, float]]
) -> np.ndarray:
    """Calculate heuristic values for ant colony optimization"""
    heuristic = np.zeros((len(orders_assign), len(picker_locations)))
    
    for item_idx, item_locs in enumerate(orders_assign):
        for picker_idx, picker_loc in enumerate(picker_locations):
            min_distance = float('inf')
            for loc in item_locs:
                distance = math.sqrt((loc[0] - picker_loc[0])**2 + 
                                  (loc[1] - picker_loc[1])**2)
                min_distance = min(min_distance, distance)
            heuristic[item_idx][picker_idx] = 1 / (min_distance + 1e-6)
            
    return heuristic

def main():
    # Initialize services
    picklist_repo = PicklistRepository()
    route_optimizer = RouteOptimizer()
    genetic_op = GeneticOperator(route_optimizer)
    
    try:
        # Get data using repository pattern
        picktasks, orders_assign, stage_result = picklist_repo.get_optimized_data()
        
        # Initialize population
        empty_pop = []
        initial_population = initialize_population(
            NUM_PICKERS, 
            len(orders_assign), 
            PICKER_CAPACITIES
        )
        
        # Evaluate initial population
        for position in initial_population:
            fitness_score, routes, _ = route_optimizer.calculate_shortest_route(
                PICKER_LOCATIONS, position, orders_assign, picktasks, stage_result
            )
            empty_pop.append([position, fitness_score])
        
        # Initialize ACO components
        pheromone = np.ones((len(orders_assign), NUM_PICKERS))
        heuristic = calculate_heuristic(orders_assign, PICKER_LOCATIONS)
        
        # Ant Colony Optimization
        for ant in range(NUM_ANTS):
            assignment = [-1] * len(orders_assign)
            picker_loads = [0] * NUM_PICKERS
            
            # Build solution
            for item in range(len(orders_assign)):
                valid_pickers = []
                prob = []
                
                for picker in range(NUM_PICKERS):
                    if picker_loads[picker] < PICKER_CAPACITIES[picker]:
                        valid_pickers.append(picker)
                        prob.append((pheromone[item][picker] ** ALPHA) * 
                                  (heuristic[item][picker] ** BETA))
                
                if valid_pickers:
                    prob = np.array(prob)
                    prob /= prob.sum()
                    chosen_picker = np.random.choice(valid_pickers, p=prob)
                    assignment[item] = chosen_picker
                    picker_loads[chosen_picker] += 1
            
            # Evaluate solution
            fitness_score, routes, _ = route_optimizer.calculate_shortest_route(
                PICKER_LOCATIONS, assignment, orders_assign, picktasks, stage_result
            )
            empty_pop.append([assignment, fitness_score])
            
            # Update pheromone trails
            for item in range(len(orders_assign)):
                if assignment[item] != -1:
                    pheromone[item][assignment[item]] *= (1 - RHO)
                    pheromone[item][assignment[item]] += 1 / fitness_score
        
        # Genetic Algorithm Optimization
        pop = sorted(empty_pop, key=lambda x: x[1])
        best_solution = pop[0]
        
        for iteration in range(MAX_IT):
            # Crossover phase
            crossover_population = []
            for _ in range(NC // 2):
                parent1 = genetic_op.tournament_selection(pop, TOURNAMENT_SIZE)
                parent2 = genetic_op.tournament_selection(pop, TOURNAMENT_SIZE)
                
                offspring1, offspring2 = genetic_op.crossover(parent1, parent2)
                
                # Evaluate offspring
                fitness1, _, _ = route_optimizer.calculate_shortest_route(
                    PICKER_LOCATIONS, offspring1, orders_assign, picktasks, stage_result
                )
                fitness2, _, _ = route_optimizer.calculate_shortest_route(
                    PICKER_LOCATIONS, offspring2, orders_assign, picktasks, stage_result
                )
                
                crossover_population.extend([
                    [offspring1, fitness1],
                    [offspring2, fitness2]
                ])
            
            # Mutation phase
            mutation_population = []
            for _ in range(NM):
                parent = random.choice(pop)[0]
                offspring = genetic_op.mutate_with_capacity(parent, PICKER_CAPACITIES)
                
                fitness, _, _ = route_optimizer.calculate_shortest_route(
                    PICKER_LOCATIONS, offspring, orders_assign, picktasks, stage_result
                )
                mutation_population.append([offspring, fitness])
            
            # Update population
            empty_pop = pop + crossover_population + mutation_population
            empty_pop.sort(key=lambda x: x[1])
            pop = empty_pop[:N_POP]
            
            new_best_solution = pop[0]
            logger.info(f"Iteration {iteration}: Best Solution = {new_best_solution[1]}")
        
        # Final solution
        final_solution = pop[0][0]
        logger.info(f"\nFinal Best Solution: {final_solution}")
        
        # Visualize results
        # graph_plot(final_solution)
        
    except Exception as e:
        logger.error(f"Error in optimization process: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()