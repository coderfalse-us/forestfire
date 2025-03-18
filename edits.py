import random
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist

rows = 100
cols = 100
num_items = 100
num_pickers = 10
MaxIt = 50
nPop = 150 #number of population
pc = 0.90;  #probability of crossover
pm = 0.04 ; #probability of mutation
nc = 2*round((nPop*pc)/2);  #No. of crossover
nm = round(nPop*pm)
beta=0.1 
TournmentSize = 5

alpha = 1.0         # Influence of pheromone trails
beta = 2.0          # Influence of heuristic information
rho = 0.5           # Evaporation rate
Q = 100             # Constant used to update the pheromone
num_ants = 25

start_row = 0
step_between_rows = 10
number_of_lines = 10
selected_rows = [start_row + i * step_between_rows for i in range(number_of_lines)]

#random.seed(42)
picker_locations = [(6, 118), (6, 47), (14, 95), (12, 22), (3, 23), (114, 76), (119, 77), (106, 31), (113, 0), (101, 43)]
item_locations=[(89, 0), (59, 0), (85, 0), (79, 0), (30, 0), (33, 0), (88, 0), (58, 0), (51, 0), (48, 0), (54, 10), (56, 10), (54, 10), (45, 10), (21, 10), (82, 10), (71, 10), (92, 10), (74, 10), (61, 10), (55, 20), (69, 20), (87, 20), (71, 20), (43, 20), (33, 20), (56, 20), (70, 20), (91, 20), (33, 20), (79, 30), (40, 30), (40, 30), (74, 30), (21, 30), (66, 30), (23, 30), (63, 30), (23, 30), (29, 30), (80, 40), (67, 40), (77, 40), (50, 40), (57, 40), (54, 40), (90, 40), (85, 40), (32, 40), (70, 40), (75, 50), (62, 50), (65, 50), (59, 50), (65, 50), (100, 50), (51, 50), (43, 50), (67, 50), (39, 50), (95, 60), (98, 60), (85, 60), (94, 60), (78, 60), (33, 60), (77, 60), (77, 60), (91, 60), (28, 60), (43, 70), (31, 70), (46, 70), (94, 70), (82, 70), (31, 70), (79, 70), (61, 70), (96, 70), (70, 70), (35, 80), (63, 80), (56, 80), (22, 80), (79, 80), (24, 80), (97, 80), (57, 80), (99, 80), (91, 80), (69, 90), (23, 90), (96, 90), (20, 90), (57, 90), (100, 90), (96, 90), (65, 90), (57, 90), (31, 90)]
picker_capacities = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
#============================================================================================================================

#                                                   -----------------
#                                                   | RANDOMIZATION |
#                                                   ----------------

# picker_locations = []
# for i in range(num_pickers//2):
#     picker_locations.append((random.randint(0,20),random.randint(0,120)))
# for i in range(num_pickers//2):
#     picker_locations.append((random.randint(100,120),random.randint(0,120)))
# item_locations = [(65, 41), (42, 66), (74, 18), (44, 54), (31, 92), (89, 11), (64, 62), (41, 38), (24, 13), (32, 59), (49, 69), (34, 38), (67, 31), (41, 82), (83, 1), (79, 90), (30, 10), (33, 100), (96, 12), (58, 71), (41, 86), (21, 29), (42, 86), (60, 14), (89, 38), (97, 63), (73, 37), (96, 14), (90, 34), (99, 15), (34, 39), (38, 70), (37, 50), (61, 45), (49, 18), (95, 1), (40, 10), (79, 97), (85, 42), (70, 39), (56, 46), (82, 18), (41, 39), (53, 33), (63, 53), (20, 23), (29, 74), (44, 52), (81, 84), (49, 53), (70, 23), (22, 26), (99, 63), (64, 80), (31, 40), (47, 78), (66, 7), (74, 33), (53, 96), (87, 72), (37, 50), (51, 67), (79, 77), (41, 96), (89, 39), (34, 76), (81, 7), (38, 26), (30, 43), (27, 9), (66, 87), (41, 2), (62, 50), (95, 70), (25, 24), (93, 1), (22, 88), (43, 61), (36, 24), (58, 43), (38, 40), (62, 83), (72, 60), (100, 48), (31, 73), (79, 21), (43, 81), (22, 28), (37, 36), (65, 69), (52, 51), (91, 26), (96, 64), (52, 50), (45, 47), (47, 48), (30, 46), (55, 32), (100, 47), (55, 67)]

# item_locations = []
# for row in selected_rows:
#     for i in range(10):
#         # Append random column positions (column_start to column_end) for the given row
#         item_locations.append((random.randint(20, 100), row))

#============================================================================================================================

# num_orders = 100

# orders = []

# for i in range(0, num_orders):

#     num_items_in_order = random.randint(1, 5)

#     selected_items = random.choices(item_locations, k=num_items_in_order)

#     orders.append(selected_items)
# orders_assign=orders[:sum(picker_capacities)]
# for order, items in enumerate(orders_assign):
#     print(f"{order}: {items}")

# print("Pending items")
# for order, items in enumerate(orders[sum(picker_capacities)::]):
#     print(f"{sum(picker_capacities)+order}: {items}")

print(picker_locations)
picker_locations1 = picker_locations.copy()




def e_d(picker_location,item_location):
        x1, y1 = picker_location
        x2, y2 = item_location
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance

def walkway_from_condition(value, left_walkway, right_walkway):
      return left_walkway if value % 20 == 0 else right_walkway
#Tournament
def tournament_selection(population, TournmentSize):

    tournament_contestants = random.sample(population, TournmentSize)
    winner = sorted(tournament_contestants, key=lambda x: x[1])[0]
    return winner[0]

#fitness with sorted paths
def calc_distance_with_shortest_route(picker_locations, item_locations, emptypop_position):

      left_walkway=15
      right_walkway=105

      order_indices = [[] for _ in range(len(picker_locations))] 
      assignments = [[] for _ in range(len(picker_locations))]
      for index, picker_index in enumerate(emptypop_position):
          assignments[picker_index].extend(orders_assign[index])
          order_indices[picker_index].append(index) 
      sorted_data = [[] for _ in range(num_pickers)]


      final_result = []
      seen = set()  # A set to track duplicates

      for i in range(len(picker_locations)):
          data = assignments[i]
          indices = order_indices[i]
          taskids = [picktasks[i] for i in indices]
            

          for taskid in taskids:
            if taskid[0] not in seen:
                seen.add(taskid[0])
                final_result.extend(stage_result.get(taskid[0], None))
          quotients = {}
          for item in data:
              quotient = item[1] // 10
              if quotient not in quotients:
                  quotients[quotient] = []
              quotients[quotient].append(item)

          for quotient in sorted(quotients.keys()):
              group = quotients[quotient]
              if quotient % 2 != 0:  # Even
                  sorted_group = sorted(group, key=lambda x: x[0], reverse=True)
              else:  # Odd
                  sorted_group = sorted(group, key=lambda x: x[0])
              sorted_data[i].extend(sorted_group)
        

      r_flag=[0]*10

      for p in range(len(picker_locations)):
        if not sorted_data[p]:
          continue

        dist1_walkway = walkway_from_condition(sorted_data[p][0][1], left_walkway, right_walkway)
        dist2_walkway = walkway_from_condition(sorted_data[p][-1][1], left_walkway, right_walkway)

        dist1 = e_d(picker_locations[p], (dist1_walkway, sorted_data[p][0][1]))
        dist2 = e_d(picker_locations[p], (dist2_walkway, sorted_data[p][-1][1]))


        if picker_locations[p][0] < 50:
          if dist1<dist2:
            sorted_data[p].insert(0,picker_locations[p])
            if sorted_data[p][1][1]%20 == 0:
              sorted_data[p].insert(1,(left_walkway,sorted_data[p][1][1]))
            else :
              sorted_data[p].insert(1,(left_walkway,sorted_data[p][1][1]-step_between_rows))
          else:
            sorted_data[p]=sorted_data[p][::-1]
            r_flag[p]=1
            sorted_data[p].insert(0,picker_locations[p])
            if sorted_data[p][1][1]%20 ==0:
              sorted_data[p].insert(1,(left_walkway,sorted_data[p][1][1]))
            else:
              sorted_data[p].insert(1,(left_walkway,sorted_data[p][1][1]+step_between_rows))
        else:
          if dist1<dist2:
            if sorted_data[p][0][1]%20 != 0:
              sorted_data[p].insert(0,picker_locations[p])
              sorted_data[p].insert(1,(right_walkway,sorted_data[p][1][1]))
            else:
              sorted_data[p].insert(0,picker_locations[p])
              sorted_data[p].insert(1,(right_walkway,sorted_data[p][1][1]-step_between_rows))
          else:
            r_flag[p]=1
            if sorted_data[p][-1][1]%20 !=0:
              sorted_data[p]=sorted_data[p][::-1]
              sorted_data[p].insert(0,picker_locations[p])
              sorted_data[p].insert(1,(right_walkway,sorted_data[p][1][1]))
            else:
              sorted_data[p]=sorted_data[p][::-1]
              sorted_data[p].insert(0,picker_locations[p])
              sorted_data[p].insert(1,(right_walkway,sorted_data[p][1][1]+step_between_rows))

         # print(r_flag)
      l=[]

      for j,k in enumerate(sorted_data):
        if not k:
              l.append([])
              continue
        l1 = k.copy()

        i = 1
        while i < len(l1) - 1:
            if l1[i][1] != l1[i + 1][1]:
                if l1[i][1] % 20 == 0:
                    if l1[i + 1][1] % 20 != 0:

                        l1.insert(i + 1, (right_walkway, l1[i][1]))
                        l1.insert(i + 2, (right_walkway, l1[i + 2][1]))
                        i += 2
                    else:
                      if r_flag[j]==0:
                        l1.insert(i + 1, (right_walkway, l1[i][1]))
                        l1.insert(i + 2, (right_walkway, (l1[i + 1][1] + step_between_rows)))
                        l1.insert(i + 3, (left_walkway, (l1[i + 2][1])))
                        l1.insert(i + 4, (left_walkway, l1[i + 4][1]))
                        i += 4
                      else:
                        l1.insert(i + 1, (right_walkway, l1[i][1]))
                        l1.insert(i + 2, (right_walkway, (l1[i + 1][1] - step_between_rows)))
                        l1.insert(i + 3, (left_walkway, (l1[i + 2][1])))
                        l1.insert(i + 4, (left_walkway, l1[i + 4][1]))
                        i += 4
                else:
                    if l1[i + 1][1] % 20 == 0:
                        l1.insert(i + 1, (left_walkway, l1[i][1]))
                        l1.insert(i + 2, (left_walkway, l1[i + 2][1]))
                        i += 2
                    else:
                      if r_flag[j]==0:
                        l1.insert(i + 1, (left_walkway, l1[i][1]))
                        l1.insert(i + 2, (left_walkway, (l1[i + 1][1] + step_between_rows))) #i+1 needed
                        l1.insert(i + 3, (right_walkway, (l1[i + 2][1])))#i+2
                        l1.insert(i + 4, (right_walkway, l1[i + 4][1]))
                        i += 4
                      else:
                        l1.insert(i + 1, (left_walkway, l1[i][1]))
                        l1.insert(i + 2, (left_walkway, (l1[i + 1][1] - step_between_rows)))
                        l1.insert(i + 3, (right_walkway, (l1[i + 2][1])))
                        l1.insert(i + 4, (right_walkway, l1[i + 4][1]))
                        i += 4
            else:
                i += 1
        l1.extend(final_result)
        print(final_result)
        l.append(l1)

      total_cost = 0
      individual_costs = []
      for points in l:
          list_cost = 0

          for i in range(len(points) - 1):
              x1, y1 = points[i]
              x2, y2 = points[i + 1]
              distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
              list_cost += distance

          individual_costs.append(list_cost)
          total_cost += list_cost

      return total_cost,l,assignments


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
def main():
    empty_pop = []
    global orders  # Make sure this variable is defined elsewhere in your code
    
    # Initial Population
    for iteration in range(25 - 1):
        emptypop_position = []

        assigned_counts = [0] * num_pickers  # Track the number of assignments per picker

        for f in range(len(orders_assign)):  # Iterate over orders_assign (list of lists of tuples)
            valid_pickers = [i for i in range(num_pickers) if assigned_counts[i] < picker_capacities[i]]

            # Randomly assign a picker to the current order while respecting capacity constraints
            picker_id = random.choice(valid_pickers)
            assigned_counts[picker_id] += 1
            emptypop_position.append(picker_id)

        # Random shuffle as part of initialization
        random.shuffle(emptypop_position)

        # Evaluate the initial solution's fitness
        fitness_score, sorted_paths, _ = calc_distance_with_shortest_route(picker_locations, orders_assign, emptypop_position)
        empty_pop.append([emptypop_position, fitness_score])  # Append individuals with their fitness

    # Initialize pheromone trails and heuristic values
    pheromone = np.ones((len(orders_assign), num_pickers))  # Orders_assign defines the number of items

    heuristic = np.zeros((len(orders_assign), num_pickers))
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
    for ant in range(num_ants):
        assignment = [-1] * len(orders_assign)  # Assignment of pickers to orders
        picker_loads = [0] * num_pickers  # Track picker loads (capacity used)

        for item in range(len(orders_assign)):
            valid_pickers = []
            prob = []

            # Identify pickers who can take the order without exceeding capacity
            for picker in range(num_pickers):
                if picker_loads[picker] < picker_capacities[picker]:
                    valid_pickers.append(picker)
                    prob.append((pheromone[item][picker] ** alpha) * (heuristic[item][picker] ** beta))

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
                pheromone[item][assignment[item]] *= (1 - rho)
                pheromone[item][assignment[item]] += 1 / fitness_score

    # Sort population by fitness and select the best solution
    pop = sorted(empty_pop, key=lambda x: x[1])
    best_solution = pop[0]

    # Genetic Algorithm Loop
    for iteration in range(MaxIt):
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

        print(f"Iteration:{iteration} Best Solution:", new_best_solution[0],new_best_solution[1])

    final_solution = new_best_solution[0]

    # Final output
    print(f"\nFinal Best Solution (Pick Assignments): {final_solution}")

    # Generate orders for each picker based on the final solution
    orders = {picker_id: [] for picker_id in range(num_pickers)}
    for item_id, picker_id in enumerate(final_solution):
        orders[picker_id].append(item_id)

    print("\nOrders for Each Picker:")
    for picker_id, items in orders.items():
        print(f"Picker {picker_id}: Orders Tasks {items}")

    # Generate **sorted paths** for plotting
    _,sorted_paths,assignments = calc_distance_with_shortest_route(picker_locations, item_locations, final_solution)

    # Plot results with sorted paths
    fig, axes = plt.subplots(nrows=1, ncols=len(picker_locations1), figsize=(30, 6), sharex=True, sharey=True)

    picker_x, picker_y = zip(*picker_locations1)  # Original picker locations
    item_x, item_y = zip(*item_locations)  # All item locations

    for group, ax in enumerate(axes):
        if group >= len(picker_locations1):  # Prevent index errors
            continue

        ax.scatter(*picker_locations1[group], c='blue', s=150, label='Picker Start', marker='o')  # Start picker locations

        ax.scatter(item_x, item_y, c='red', s=50, label='Items', marker='*')

        if group < len(sorted_paths):
            points = [picker_locations1[group]] + sorted_paths[group]

            if len(points) > 1:
                x, y = zip(*points)
                ax.plot(x, y, label=f'Picker {group + 1} Path', linestyle='-', linewidth=2)

        if group < len(assignments):
            assignment_points = assignments[group]
        if assignment_points:
            assign_x, assign_y = zip(*assignment_points)
            ax.scatter(assign_x, assign_y, c='green', s=60, label='Assigned Items', marker='o')

        ax.set_title(f"Picker {group + 1}", fontsize=12)
        ax.set_xlabel("X Coordinate", fontsize=10)
        ax.set_ylabel("Y Coordinate", fontsize=10)
        ax.grid(True)

main()