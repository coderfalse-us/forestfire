from forestfire.utils.config import *
from forestfire.algorithms.genetic import GeneticAlgorithm
from forestfire.algorithms.aco import AntColony
from forestfire.optimizer.fitness import FitnessCalculator
from forestfire.visualization.plot import plot_solution
import numpy as np

def main():
    # Initialize components
    ga = GeneticAlgorithm(
        pop_size=POPULATION_SIZE,
        crossover_prob=CROSSOVER_PROB,
        mutation_prob=MUTATION_PROB,
        tournament_size=TOURNAMENT_SIZE,
        picker_capacities=PICKER_CAPACITIES
    )
    
    aco = AntColony(
        num_ants=NUM_ANTS,
        alpha=ALPHA,
        beta=BETA,
        rho=RHO,
        q_value=Q
    )
    
    fitness = FitnessCalculator(
        picker_locations=PICKER_LOCATIONS,
        picker_capacities=PICKER_CAPACITIES
    )
    
    # Initial population from ACO
    pheromone = aco.initialize_pheromone(NUM_ITEMS, NUM_PICKERS)
    population = []
    
    # ACO Phase - Generate initial solutions
    for _ in range(POPULATION_SIZE):
        solution = aco.construct_solution(pheromone)
        score = fitness.evaluate(solution)
        population.append(solution)
        aco.update_pheromone(pheromone, solution, score)
    
    # Track best solution
    best_solution = None
    best_score = float('inf')
    
    # GA Phase - Improve solutions
    for iteration in range(MAX_ITERATIONS):
        # Generate new solutions
        offspring = ga.crossover(population)
        mutants = ga.mutate(population)
        
        # Combine and evaluate all solutions
        combined_pop = population + offspring + mutants
        population = ga.select_next_generation(combined_pop, fitness)
        
        # Update best solution
        current_best = min(population, key=lambda x: fitness.evaluate(x))
        current_score = fitness.evaluate(current_best)
        
        if current_score < best_score:
            best_solution = current_best
            best_score = current_score
            
        print(f"Iteration {iteration}: Best Score = {best_score:.2f}")
    
    # Calculate and display final solution details
    final_cost, final_paths, assignments = fitness.calculate_solution_fitness(best_solution)
    print(f"\nFinal Solution:")
    print(f"Total Distance: {final_cost:.2f}")
    print(f"Items per Picker: {[len(a) for a in assignments]}")
    
    # Visualize result
    plot_solution(best_solution, PICKER_LOCATIONS, item_locations=ITEM_LOCATIONS)

if __name__ == "__main__":
    main()