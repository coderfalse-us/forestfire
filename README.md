# Picker Order Optimization System

## Overview

This project provides an implementation of a picker order optimization system to efficiently address the **Warehouse Picker Routing Problem**. It uses a combination of **Genetic Algorithms (GA)** and **Ant Colony Optimization (ACO)** to assign items to pickers while ensuring optimized paths.

The designed system minimizes total distance traveled by pickers in a warehouse by selecting the best assignments of items to pickers, incorporating picker capacities, and producing warehouse routes in a structured and logical manner. 

## Objectives

1. **Minimize Total Distance Traveled:** Optimize picker paths to reduce cumulative picking distance and save time.
2. **Ensure Picker Capacity Constraints:** Manage picker assignments, ensuring their capacity isn't exceeded.
3. **Route Optimization:** Address the layout design of a warehouse with walkways and cross-segments.
4. **Simulate & Visualize:** Visualize picker assignments and paths for better insights.

---

## Features

- **Picker Assignment:** Assigns items to warehouse pickers.
- **Fitness Function:** Evaluates picker assignments by computing total distances traveled, considering warehouse constraints.
- **Path Optimization:** Sorts picker paths to minimize unnecessary travel.
- **Genetic Algorithm:** 
  - Crossover and mutation operators to evolve solutions over iterations.
  - Capacity-based picker constraints in mutation and crossover.
  - Tournament selection for selecting parents.
- **Ant Colony Optimization:** Assigns items intelligently by considering heuristic and pheromone values.
- **Database Querying:** Extract warehouse data such as tasks, items, and staging areas from PostgreSQL tables.
- **Visualization:** Visualize picker paths and assignments in graphs using `matplotlib`.

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repository.git
   cd your-repository
   ```

2. **Install dependencies**:
   Install required Python libraries using pip:
   ```bash
   pip install -r requirements.txt
   ```
   Required libraries:
   - `random`: To generate random initial populations and item assignments.
   - `math`: For mathematical calculations like Euclidean distance.
   - `numpy`: To handle arrays and perform calculations efficiently.
   - `scipy`: To compute spatial distances.
   - `matplotlib`: To visualize picker assignments and routing paths.
   - `psycopg2`: For extracting pick tasks and item details from PostgreSQL.

3. **Database configuration**:  
   Update the PostgreSQL connection details in `db_c()`:
   ```python
   DB_HOST = "<your-db-host>"
   DB_NAME = "<your-db-name>"
   DB_USER = "<your-db-user>"
   DB_PASSWORD = "<your-db-password>"
   DB_PORT = "<your-db-port>"
   ```

---

## How It Works

1. **Warehouse Data Inputs**:
   - Picker locations, item locations, and item picking tasks are fetched through `db_c()`.
   - Details are stored in the form of dictionaries/lists.

2. **Model Configuration**:
   - Parameters such as number of pickers, picker capacities, warehouse layout (walkways), and optimization algorithm hyperparameters are defined.

3. **Fitness Evaluation**:
   - Calculates the Euclidean distances between picker locations and assigned items.
   - Ensures picker paths optimize their distance by following walkways/cross-segments.

4. **Optimization Process**:
   - **Initial Solution**:
     - Random initial population of picker-to-item assignments.
     - Evaluate each solution's fitness by calculating total traveled distances.
   - **Ant Colony Optimization**:
     - Compute heuristic (inverse distance) and pheromone values for each item.
     - Build an initial solution guided by these parameters.
   - **Genetic Algorithm**:
     - Evolve the solution over a number of iterations:
       - **Tournament Selection**: Select top individuals from the population.
       - **Crossover**: Combine parent solutions (single-point & uniform).
       - **Mutation**: Alter solutions to maintain diversity while enforcing capacity constraints.
   - **Best Solution**: Retrieve and plot the best picker assignments.

---

## Files and Structure

### Key Files

1. **picker_optimization.py**:  
   Main code that implements the optimization pipeline.

2. **requirements.txt**:  
   List of dependencies used in the project.

3. **README.md**:  
   Documentation (this file).

### Key Functions

1. **`db_c()`**:  
   Fetches item picking tasks and picker details from PostgreSQL database.

2. **`calc_distance_with_shortest_route()`**:  
   Calculates the fitness (distance traveled) for picker orders based on sorted paths.

3. **`tournament_selection()`**:  
   Selects parent solutions at each generation based on tournament size.

4. **`crossover()`**:  
   Combines two parent solutions to create offspring.

5. **`mutate_with_capacity()`**:  
   Mutates a solution while ensuring picker capacities are respected.

---

## Usage

1. **Run the Script**:
   Execute the script via terminal:
   ```bash
   python picker_optimization.py
   ```

2. **View Outputs**:
   - Picker assignments for items.
   - Total distance traveled after optimization.
   - Visual plots of picker paths per picker.

3. **Modify Parameters**:
   Customize parameters like picker locations, capacities, ACO/GA hyperparameters (`pc`, `pm`, `num_ants`, etc.), or warehouse layout (starting rows, walkway step).

---

## Key Parameters & Customizations

| **Parameter**                 | **Description**                                                                                     | **Default Value**      |
|-------------------------------|-----------------------------------------------------------------------------------------------------|------------------------|
| `num_pickers`                 | Total number of pickers in the warehouse.                                                           | `10`                   |
| `picker_capacities`           | A list of picker capacities (number of items each picker can handle).                               | `[10, 10, ..., 10]`    |
| `num_items`                   | Total number of items to be picked.                                                                 | `100`                  |
| `MaxIt`                       | Maximum number of iterations for the genetic algorithm.                                             | `50`                   |
| `nPop`                        | Population size for the genetic algorithm.                                                          | `150`                  |
| `pc (probability crossover)`  | Crossover rate for genetic algorithm.                                                               | `0.90`                 |
| `pm (probability mutation)`   | Mutation rate for genetic algorithm.                                                                | `0.04`                 |
| `num_ants`                    | Number of ants in the ant colony optimization algorithm.                                            | `25`                   |
| `rho`                         | Pheromone evaporation rate (used in ACO).                                                           | `0.5`                  |
| `alpha`                       | Influence of pheromone trails in ACO.                                                               | `1.0`                  |
| `beta`                        | Influence of heuristic information (1/distance) in ACO.                                             | `2.0`                  |
| `start_row`                   | Starting row position in the warehouse layout for items/lines.                                      | `0`                    |
| `step_between_rows`           | Distance between rows in warehouse layout.                                                          | `10`                   |
| `picker_locations`            | List of fixed picker start locations (x, y).                                                        | Predefined Coordinates |

---

## Visualization

- Each picker is assigned items and a route for optimization.
- Visualizations include:
  1. Picker start locations (blue markers).
  2. All item locations (red markers).
  3. Picker travel path (brown lines connecting items).

---

## Improvements & Future Work

1. **Dynamic Layout Adaptability:** Extend the system to adapt different warehouse layouts (e.g., uneven rows, zones).
2. **Multi-Objective Optimization:** Incorporate additional objectives such as picker workload balancing or time-based constraints.
3. **Real-Time Integration:** Connect to warehouse systems for real-time item locations and route updates.
4. **Improved Crossover & Mutation:** Use more sophisticated crossovers and adaptive mutation rates.

---

## License

This project is licensed under the MIT License. Feel free to use or modify it for your use case.

---

## Contact & Support

For any questions or support, please reach out to:
- **Email**: [youremail@example.com](mailto:youremail@example.com)
- **GitHub Issues**: [Submit an Issue](https://github.com/your-repository/issues)

Happy Optimizing! 🚀