# ForestFire - Warehouse Order Picking Optimization

## Overview

ForestFire is a robust implementation of a warehouse order picking optimization system that efficiently addresses the **Warehouse Picker Routing Problem**. It uses a combination of **Genetic Algorithms (GA)** and **Ant Colony Optimization (ACO)** to assign items to pickers while ensuring optimized paths.

The system minimizes total distance traveled by pickers in a warehouse by selecting the best assignments of items to pickers, incorporating picker capacities, and producing warehouse routes in a structured and logical manner. The codebase follows clean architecture principles with high test coverage (>90%) and adheres to the Google style guide for Python.

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
   git clone https://github.com/forestfire.git
   cd forestfire
   ```

2. **Install dependencies**:
   Install required Python libraries using pip:
   ```bash
   pip install -r requirements.txt
   ```
   Required libraries:
   - `numpy`: For efficient array operations and calculations
   - `matplotlib`: For visualizing picker assignments and routing paths
   - `psycopg2`: For PostgreSQL database connectivity
   - `pytest`: For running unit tests
   - `pytest-cov`: For measuring test coverage

3. **Database configuration**:
   Update the PostgreSQL connection details in `forestfire/database/config.py`:
   ```python
   DB_HOST = "<your-db-host>"
   DB_NAME = "<your-db-name>"
   DB_USER = "<your-db-user>"
   DB_PASSWORD = "<your-db-password>"
   DB_PORT = "<your-db-port>"
   ```

4. **Run tests**:
   ```bash
   python -m pytest
   ```

   To check test coverage:
   ```bash
   python -m pytest --cov=forestfire
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

## Project Structure

### Key Directories

1. **`forestfire/`**:
   Main package containing all modules.

   - **`algorithms/`**: Implementation of optimization algorithms
     - `ant_colony.py`: Ant Colony Optimization algorithm
     - `genetic.py`: Genetic Algorithm implementation

   - **`database/`**: Database connectivity and repository pattern
     - `config.py`: Database configuration
     - `connection.py`: Database connection management
     - `repository.py`: Base repository class
     - `services/`: Service layer for database operations
       - `picklist.py`: Repository for picklist data
       - `batch_pick_seq_service.py`: Service for batch pick sequences

   - **`optimizer/`**: Core optimization logic
     - `models/`: Data models
       - `route.py`: Route representation
     - `services/`: Optimization services
       - `routing.py`: Route optimization logic
       - `distance.py`: Distance calculation utilities

   - **`plots/`**: Visualization utilities
     - `graph.py`: Path visualization

   - **`utils/`**: Utility functions and configuration
     - `config.py`: Global configuration parameters

2. **`tests/`**:
   Comprehensive test suite with >90% coverage.

3. **`main.py`**:
   Entry point that orchestrates the optimization process.

4. **`requirements.txt`**:
   List of dependencies used in the project.

5. **`README.md`**:
   Documentation (this file).

### Key Classes and Functions

1. **`AntColonyOptimizer`**:
   Implements ant colony optimization for item-to-picker assignment.

2. **`GeneticOperator`**:
   Provides genetic algorithm operations like crossover and mutation.

3. **`RouteOptimizer`**:
   Calculates optimal routes for pickers based on assigned items.

4. **`PicklistRepository`**:
   Fetches and processes picklist data from the database.

5. **`PathVisualizer`**:
   Visualizes picker routes and assignments.

---

## Usage

1. **Run the Optimization**:
   Execute the main script via terminal:
   ```bash
   python main.py
   ```

2. **View Outputs**:
   - Picker assignments for items
   - Total distance traveled after optimization
   - Visual plots of picker paths in the `output` directory

3. **Modify Parameters**:
   Customize parameters in `forestfire/utils/config.py`:
   - `NUM_PICKERS`: Number of pickers in the warehouse
   - `PICKER_CAPACITIES`: Capacity constraints for each picker
   - `MAX_ITERATIONS`: Maximum number of iterations for optimization
   - `POPULATION_SIZE`: Size of the population for genetic algorithm
   - `CROSSOVER_RATE`: Probability of crossover in genetic algorithm
   - `MUTATION_RATE`: Probability of mutation in genetic algorithm
   - `NUM_ANTS`: Number of ants in ACO algorithm
   - `ALPHA`: Pheromone importance factor in ACO
   - `BETA`: Heuristic importance factor in ACO
   - `RHO`: Pheromone evaporation rate in ACO

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

## Recent Improvements

1. **Code Architecture:** Refactored to follow clean architecture principles with proper separation of concerns.
2. **Test Coverage:** Achieved >90% test coverage with comprehensive unit tests.
3. **Code Quality:** Implemented Google style guide for consistent code formatting.
4. **Database Access:** Implemented repository pattern with read-only database sessions to prevent accidental data insertion.

## Future Work

1. **Dynamic Layout Adaptability:** Extend the system to adapt to different warehouse layouts (e.g., uneven rows, zones).
2. **Multi-Objective Optimization:** Incorporate additional objectives such as picker workload balancing or time-based constraints.
3. **Real-Time Integration:** Connect to warehouse systems for real-time item locations and route updates.
4. **Improved Crossover & Mutation:** Implement more sophisticated crossovers and adaptive mutation rates.
5. **Performance Optimization:** Enhance algorithm performance for larger warehouses and more complex scenarios.

---

## License

This project is licensed under the MIT License. Feel free to use or modify it for your use case.

---

## Contact & Support

For any questions or support, please reach out to:
- **GitHub Issues**: [Submit an Issue](https://github.com/forestfire/issues)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and ensure tests pass (`python -m pytest`)
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Happy Optimizing! 🚀🚢