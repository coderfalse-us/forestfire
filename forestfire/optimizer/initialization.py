from forestfire.optimizer.utils import calc_distance_with_shortest_route
from forestfire.utils import config
from forestfire.database.picklist import getdata

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

    fitness_score, sorted_paths,_ = calc_distance_with_shortest_route(picker_locations, emptypop_position, orders_assign, picktasks, stage_result)
    empty_pop.append([emptypop_position, fitness_score])  # Append individuals with their fitness

pheromone = np.ones((len(orders_assign), NUM_PICKERS))  # Orders_assign defines the number of items

heuristic = np.zeros((len(orders_assign), NUM_PICKERS))
for item_idx, item_locs in enumerate(orders_assign):  # Each order is a list of tuple locations
    for picker_idx, picker_loc in enumerate(picker_locations):
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
    fitness_score, sorted_paths, _ = calc_distance_with_shortest_route(picker_locations, orders_assign, assignment)
    empty_pop.append([assignment, fitness_score])

    # Update pheromone trails
    for item in range(len(orders_assign)):
        if assignment[item] != -1:
            pheromone[item][assignment[item]] *= (1 - RHO)
            pheromone[item][assignment[item]] += 1 / fitness_score

pop = sorted(empty_pop, key=lambda x: x[1])  # Sort population by fitness
best_solution = pop[0]

