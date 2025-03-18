import random

# Algorithm parameters
NUM_PICKERS = 10
NUM_ITEMS = 100
MAX_ITERATIONS = 50
POPULATION_SIZE = 150
CROSSOVER_PROB = 0.90
MUTATION_PROB = 0.04
TOURNAMENT_SIZE = 5

# ACO parameters
ALPHA = 1.0  # Pheromone influence
BETA = 2.0   # Heuristic influence 
RHO = 0.5    # Evaporation rate
Q = 100      # Pheromone deposit factor
NUM_ANTS = 25

# Warehouse layout
ROWS = 100
COLS = 100
LEFT_WALKWAY = 15
RIGHT_WALKWAY = 105
STEP_BETWEEN_ROWS=10

# Fixed locations
PICKER_LOCATIONS = [(6, 118), (6, 47), (14, 95), (12, 22), (3, 23), 
                    (114, 76), (119, 77), (106, 31), (113, 0), (101, 43)]
PICKER_CAPACITIES = [10] * NUM_PICKERS