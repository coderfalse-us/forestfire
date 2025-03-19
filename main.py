from forestfire.optimizer.fitness import calc_distance_with_shortest_route
from forestfire.utils import config
from forestfire.database.picklist import getdata
from forestfire.algorithms.genetic import mutate_with_capacity, crossover, tournament_selection
from forestfire.utils.config import *
import random
import numpy as np
import math

empty_pop = []

global orders

picktasks,orders_assign,stage_result = getdata()
# Initial Population
for iteration in range(25-1):
    emptypop_position = []

    assigned_counts = [0] * NUM_PICKERS
    
    for f in range(len(orders_assign)):
        valid_pickers = [i for i in range(NUM_PICKERS) if assigned_counts[i] < PICKER_CAPACITIES[i]]

        picker_id = random.choice(valid_pickers)
        assigned_counts[picker_id] += 1
        emptypop_position.append(picker_id)

    random.shuffle(emptypop_position)

    fitness_score, sorted_paths,_ = calc_distance_with_shortest_route(PICKER_LOCATIONS, emptypop_position, orders_assign, picktasks, stage_result)
    empty_pop.append([emptypop_position, fitness_score])  # Append individuals with their fitness

pheromone = np.ones((len(orders_assign), NUM_PICKERS))  # Orders_assign defines the number of items

heuristic = np.zeros((len(orders_assign), NUM_PICKERS))
for item_idx, item_locs in enumerate(orders_assign):  # Each order is a list of tuple locations
    for picker_idx, picker_loc in enumerate(PICKER_LOCATIONS):
        # Calculate distance from picker to each location in the current order
        # Assuming that each order contains one or more tuple locations
        min_distance = float('inf')
        for loc in item_locs:
            distance = math.sqrt((loc[0] - picker_loc[0]) ** 2 + (loc[1] - picker_loc[1]) ** 2)
            min_distance = min(min_distance, distance)
        heuristic[item_idx][picker_idx] = 1 / (min_distance + 1e-6)

# Ant colony optimization
for ant in range(NUM_ANTS):
    assignment = [-1] * len(orders_assign)  # Assignment of pickers to orders
    picker_loads = [0] * NUM_PICKERS  # Track picker loads (capacity used)

    for item in range(len(orders_assign)):
        valid_pickers = []
        prob = []

        # Identify pickers who can take the order without exceeding capacity
        for picker in range(NUM_PICKERS):
            if picker_loads[picker] < PICKER_CAPACITIES[picker]:
                valid_pickers.append(picker)
                prob.append((pheromone[item][picker] ** ALPHA) * (heuristic[item][picker] ** BETA))

        if valid_pickers:
            prob = np.array(prob)
            prob /= prob.sum()  # Normalize probabilities
            chosen_picker = np.random.choice(valid_pickers, p=prob)  # Select picker based on probabilities
            assignment[item] = chosen_picker
            picker_loads[chosen_picker] += 1
        else:
            # If no picker can handle the order, leave it unassigned
            # Optional: Handle unassigned orders later
            assignment[item] = -1  # '-1' indicates the order was not assigned

    # Evaluate the solution
    fitness_score, sorted_paths, _ = calc_distance_with_shortest_route(PICKER_LOCATIONS, emptypop_position, orders_assign, picktasks, stage_result)
    empty_pop.append([assignment, fitness_score])

    # Update pheromone trails
    for item in range(len(orders_assign)):
        if assignment[item] != -1:
            pheromone[item][assignment[item]] *= (1 - RHO)
            pheromone[item][assignment[item]] += 1 / fitness_score

pop = sorted(empty_pop, key=lambda x: x[1])  # Sort population by fitness
best_solution = pop[0]

for iteration in range(MAX_IT):
        crossover_population = []

        # Crossover
        for c in range(NC // 2):
            parent1 = tournament_selection(pop, TOURNAMENT_SIZE)
            parent2 = tournament_selection(pop, TOURNAMENT_SIZE)

            # parent1 = pop[0][0]
            # parent2 = pop[0][0]

            offspring1_position, offspring2_position = crossover(parent1, parent2)

            offspring1_fitness, _,_ = calc_distance_with_shortest_route(PICKER_LOCATIONS, offspring1_position, orders_assign, picktasks, stage_result)
            offspring2_fitness, _,_ = calc_distance_with_shortest_route(PICKER_LOCATIONS, offspring2_position, orders_assign, picktasks, stage_result)

            crossover_population.append([offspring1_position, offspring1_fitness])
            crossover_population.append([offspring2_position, offspring2_fitness])

        empty_pop.extend(crossover_population)

        # Mutation
        mutation_population = []
        for c in range(NM):
            parent = random.choice(pop)[0]
            offspring_position = mutate_with_capacity(parent, PICKER_CAPACITIES)

            offspring_fitness, _,_ = calc_distance_with_shortest_route(PICKER_LOCATIONS, offspring_position, orders_assign, picktasks, stage_result)

            mutation_population.append([offspring_position, offspring_fitness])

        empty_pop.extend(mutation_population)

        # Select the next generation
        empty_pop = sorted(empty_pop, key=lambda x: x[1])
        pop = empty_pop[:N_POP]  # Only take the top `nPop` individuals
        new_best_solution = pop[0]

        print(f"Iteration:{iteration} Best Solution:", new_best_solution[0],new_best_solution[1])

final_solution = new_best_solution[0]

# Final output
print(f"\nFinal Best Solution (Pick Assignments): {final_solution}")