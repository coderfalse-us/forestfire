def crossover(x1, x2):

    q = random.uniform(0, 1)

    if q <= pc:

        g = random.randint(1, 2)

        if g == 1:
            y1, y2 = single_point_crossover(x1, x2)
        elif g == 2:
            y1, y2 = uniform_crossover(x1, x2)

        # Ensure offspring satisfy picker capacity constraints
        y1 = enforce_capacity_constraints(y1, picker_capacities)
        y2 = enforce_capacity_constraints(y2, picker_capacities)

    else:

        y1 = x1[:]
        y2 = x2[:]

    return y1, y2


def single_point_crossover(x1, x2):

    n = len(x1)

    crossover_point = random.randint(1, n - 1)

    y1 = x1[:crossover_point] + x2[crossover_point:]
    y2 = x2[:crossover_point] + x1[crossover_point:]

    return y1, y2


def uniform_crossover(x1, x2):

    n = len(x1)
    y1 = []
    y2 = []

    for i in range(n):
        if random.random() < 0.5:
            y1.append(x1[i])
            y2.append(x2[i])
        else:
            y1.append(x2[i])
            y2.append(x1[i])

    return y1, y2


def enforce_capacity_constraints(offspring, picker_capacities):

    # Count how many items are currently assigned to each picker
    assigned_counts = [0] * num_pickers
    for picker_id in offspring:
        assigned_counts[picker_id] += 1

    # Identify pickers that are over their capacity
    over_capacity = {picker_id: count - picker_capacities[picker_id]
                     for picker_id, count in enumerate(assigned_counts) if count > picker_capacities[picker_id]}

    # Reassign items from over-capacity pickers
    for i, picker_id in enumerate(offspring):
        if picker_id in over_capacity and over_capacity[picker_id] > 0:
            # Find a valid picker with available capacity
            valid_pickers = [p for p in range(num_pickers) if assigned_counts[p] < picker_capacities[p]]

            if valid_pickers:
                # Reassign the item to a valid picker
                new_picker = random.choice(valid_pickers)
                offspring[i] = new_picker

                # Update counts
                assigned_counts[picker_id] -= 1
                assigned_counts[new_picker] += 1
                over_capacity[picker_id] -= 1

    return offspring

def mutate_with_capacity(x, picker_capacities):
    y = x[:]
    attempts = 10

    while attempts > 0:  # Try mutating while respecting capacity
        j = np.random.randint(len(x))
        assigned_picker = y[j]
        new_picker = np.random.randint(num_pickers)

        y[j] = new_picker

        # Check capacity constraint
        assigned_counts = [y.count(picker_id) for picker_id in range(num_pickers)]
        if all(assigned_counts[picker_id] <= picker_capacities[picker_id] for picker_id in range(num_pickers)):
            return y  # Valid mutation found

        # Revert and try again
        y[j] = assigned_picker
        attempts -= 1

    return x
def genetic():
        crossover_population = []

        # Crossover
        for c in range(nc // 2):
            parent1 = tournament_selection(pop, TournmentSize)
            parent2 = tournament_selection(pop, TournmentSize)

            # parent1 = pop[0][0]
            # parent2 = pop[0][0]

            offspring1_position, offspring2_position = crossover(parent1, parent2)

            offspring1_fitness, _,_ = calc_distance_with_shortest_route(picker_locations, item_locations, offspring1_position)
            offspring2_fitness, _,_ = calc_distance_with_shortest_route(picker_locations, item_locations, offspring2_position)

            crossover_population.append([offspring1_position, offspring1_fitness])
            crossover_population.append([offspring2_position, offspring2_fitness])

        empty_pop.extend(crossover_population)

        # Mutation
        mutation_population = []
        for c in range(nm):
            parent = random.choice(pop)[0]
            offspring_position = mutate_with_capacity(parent, picker_capacities)

            offspring_fitness, _,_ = calc_distance_with_shortest_route(picker_locations, item_locations, offspring_position)

            mutation_population.append([offspring_position, offspring_fitness])

        empty_pop.extend(mutation_population)

        # Select the next generation
        empty_pop = sorted(empty_pop, key=lambda x: x[1])
        pop = empty_pop[:nPop]  # Only take the top `nPop` individuals
        new_best_solution = pop[0]