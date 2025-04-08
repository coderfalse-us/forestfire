# Forest Fire Optimization Tests

This directory contains unit tests for the Forest Fire Optimization project.

## Test Structure

The tests are organized by component:

- `test_initialization.py`: Tests for population initialization functions
- `test_genetic_algorithm.py`: Tests for genetic algorithm operations
- `test_ant_colony.py`: Tests for ant colony optimization operations
- `test_route_optimizer.py`: Tests for route optimization logic
- `test_distance_calculator.py`: Tests for distance calculation utilities
- `test_database_services.py`: Tests for database services with mocked connections
- `test_main.py`: Tests for the main execution flow
- `test_walkway_calculator.py`: Tests for walkway calculation utilities

## Running Tests

### Running All Tests

To run all tests, use pytest:

```bash
pytest
```

### Running Specific Test Files

To run tests from a specific file:

```bash
pytest tests/test_initialization.py
```

### Running Specific Test Cases

To run a specific test case:

```bash
pytest tests/test_initialization.py::TestInitialization::test_initialize_population_size
```

## Test Configuration

The `conftest.py` file contains fixtures that are shared across multiple test files:

- `mock_database_connection`: Automatically mocks database connections for all tests
- `sample_picker_locations`: Provides sample picker locations
- `sample_orders_assign`: Provides sample order assignments
- `sample_picktasks`: Provides sample picktask IDs
- `sample_stage_result`: Provides sample staging locations
- `sample_emptypop_position`: Provides sample picker assignments
- `sample_picker_capacities`: Provides sample picker capacities

## Writing New Tests

When adding new tests:

1. Create a new test file or add to an existing one based on the component being tested
2. Use the appropriate fixtures from `conftest.py` when needed
3. Follow the existing pattern of using `unittest.TestCase` for test classes
4. Use descriptive test method names that explain what is being tested
5. Add appropriate assertions to verify expected behavior

## Mocking External Dependencies

The tests use Python's `unittest.mock` module to mock external dependencies:

- Database connections are automatically mocked via the `mock_database_connection` fixture
- Service dependencies are mocked in individual test files as needed
- Random functions are mocked when testing non-deterministic behavior

## Test Coverage

To generate a test coverage report:

```bash
pytest --cov=forestfire tests/
```

For a detailed HTML report:

```bash
pytest --cov=forestfire --cov-report=html tests/
```

This will create a `htmlcov` directory with the coverage report.
