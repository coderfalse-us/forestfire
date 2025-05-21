# Testing Libraries in ForestFire

## Overview

This document provides a comprehensive overview of the testing libraries used in the ForestFire project, their benefits, and how they are configured. Testing is a critical component of our development process, ensuring code quality, reliability, and maintainability.

## Primary Testing Libraries

### 1. pytest

**pytest** is our primary testing framework, chosen for its simplicity, powerful features, and extensive ecosystem.

#### Key Features

- **Simple syntax**: Write tests as regular Python functions with clear assertions
- **Fixture system**: Powerful dependency injection for test setup and teardown
- **Parameterization**: Run the same test with different inputs
- **Plugin ecosystem**: Extend functionality with a wide range of plugins
- **Auto-discovery**: Automatically finds and runs tests based on naming conventions

#### Configuration

Our pytest configuration is defined in `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --verbose --cov=forestfire --cov=main --cov-report=term --cov-report=html
```

This configuration:
- Looks for tests in the `tests` directory
- Identifies test files that match the pattern `test_*.py`
- Recognizes test classes that start with `Test`
- Recognizes test functions that start with `test_`
- Runs tests verbosely with coverage reporting

#### Benefits

- **Readability**: Tests are easy to write and understand
- **Maintainability**: Simple syntax reduces cognitive load
- **Productivity**: Less boilerplate code compared to other frameworks
- **Extensibility**: Easily extended with plugins and fixtures

### 2. pytest-cov

**pytest-cov** is a pytest plugin that integrates with the coverage.py library to measure code coverage during test execution.

#### Key Features

- **Subprocess support**: Tracks coverage in subprocesses without additional configuration
- **Multiple report formats**: Generates reports in various formats (terminal, HTML, XML)
- **Configurable thresholds**: Set minimum coverage requirements
- **Path inclusion/exclusion**: Control which files are included in coverage analysis

#### Configuration

Our coverage configuration is integrated with pytest through command-line options in `pytest.ini`:

```ini
addopts = --verbose --cov=forestfire --cov=main --cov-report=term --cov-report=html
```

This configuration:
- Measures coverage for the `forestfire` package and `main.py`
- Generates a terminal report for immediate feedback
- Creates an HTML report for detailed analysis

#### Benefits

- **Quality assurance**: Identifies untested code
- **Regression prevention**: Ensures new code is properly tested
- **Documentation**: Coverage reports help understand code behavior
- **Confidence**: High coverage provides confidence in code reliability

### 3. unittest.mock

**unittest.mock** is a built-in Python library for creating mock objects, used extensively in our tests to isolate components and simulate behavior.

#### Key Features

- **Mock objects**: Replace real objects with controlled test doubles
- **Spies**: Track calls to functions and methods
- **Return value control**: Specify what mock functions should return
- **Side effect simulation**: Simulate exceptions or complex behaviors

#### Usage Example

```python
from unittest.mock import patch, MagicMock

@patch("main.PicklistRepository")
def test_function(mock_picklist_repo):
    mock_picklist_repo.return_value.get_data.return_value = ["test_data"]
    # Test code that uses PicklistRepository
```

#### Benefits

- **Isolation**: Test components independently
- **Determinism**: Control external dependencies for predictable tests
- **Speed**: Avoid slow operations like database access
- **Coverage**: Test error conditions that are difficult to trigger naturally

## Additional Testing Tools

### 1. Behave (BDD Framework)

**Behave** is a Behavior-Driven Development (BDD) framework that we use for end-to-end integration testing. It allows us to write tests in a natural language format that can be understood by both technical and non-technical stakeholders.

#### Key Features

- **Gherkin syntax**: Write tests in a human-readable format
- **Feature files**: Describe system behavior from the user's perspective
- **Step definitions**: Implement test logic in Python
- **Context sharing**: Share data between test steps
- **Hooks**: Set up and tear down test environments

#### Usage Example

```gherkin
# Feature file (warehouse_optimization.feature)
Feature: Warehouse Order Picking Optimization

  Scenario: Complete optimization workflow
    Given the warehouse data is loaded from the database
    When the optimization process is executed
    Then the best solution should be valid and optimized
```

```python
# Step definition
@given("the warehouse data is loaded from the database")
def step_given_warehouse_data(context):
    context.picklist_repo = PicklistRepository()
    # Load data...
```

For more details, see the [BDD Testing Guide](bdd_testing.md).

### 2. pytest-asyncio

**pytest-asyncio** is a pytest plugin for testing asynchronous code, used in our project for testing async functions.

#### Key Features

- **Async fixtures**: Create async setup and teardown functions
- **Async test functions**: Write tests as async functions
- **Event loop management**: Properly handles event loops for testing

#### Usage Example

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected_value
```

### 3. numpy.testing

**numpy.testing** provides specialized assertions for numerical operations, which we use for testing mathematical components.

#### Key Features

- **Array comparisons**: Compare arrays with appropriate tolerances
- **Approximate equality**: Test floating-point values with tolerance
- **Shape checking**: Verify array dimensions

## Test Organization

Our tests are organized following these principles:

1. **Test location**: All tests are in the `tests` directory
2. **Test naming**: Test files are named `test_*.py`
3. **Test classes**: Test classes are named `Test*` and group related tests
4. **Test functions**: Test functions are named `test_*` and test specific behaviors

## Fixtures

We use pytest fixtures extensively to set up test environments and provide test data. Our main fixtures are defined in `tests/conftest.py`:

```python
@pytest.fixture
def route_optimizer():
    """Fixture for RouteOptimizer instance."""
    return RouteOptimizer()

@pytest.fixture
def genetic_operator(route_optimizer):
    """Fixture for GeneticOperator instance."""
    return GeneticOperator(route_optimizer)

@pytest.fixture
def sample_orders_assign():
    """Fixture for sample orders assignment data."""
    return [
        [(10, 20), (15, 25)],
        [(30, 40), (35, 45)],
        # ...
    ]
```

## Best Practices

### General Testing Practices

1. **High coverage**: We aim for >90% test coverage
2. **Isolated tests**: Tests should not depend on each other
3. **Fast execution**: Tests should run quickly
4. **Clear assertions**: Each test should have clear assertions
5. **Descriptive names**: Test names should describe what they're testing

### BDD-Specific Practices

1. **Business language**: Write scenarios in language that stakeholders understand
2. **Focus on behavior**: Describe what the system should do, not how it does it
3. **One behavior per scenario**: Each scenario should test one specific behavior
4. **Independent scenarios**: Scenarios should be able to run independently
5. **Consistent terminology**: Use consistent terminology across feature files

## Running Tests

### Unit and Integration Tests

To run the pytest test suite:

```bash
python -m pytest
```

To check test coverage:

```bash
python -m pytest --cov=forestfire
```

To generate an HTML coverage report:

```bash
python -m pytest --cov=forestfire --cov-report=html
```

### BDD Tests

To run all BDD tests:

```bash
behave
```

To run a specific feature file:

```bash
behave features/warehouse_optimization.feature
```

To run a specific scenario by name:

```bash
behave -n "Complete optimization workflow with API integration"
```

To generate a JUnit report for BDD tests:

```bash
behave --junit
```

## Conclusion

Our testing approach combines the simplicity and power of pytest for unit and integration testing with the expressiveness of Behave for BDD-style end-to-end testing. This multi-layered testing strategy, enhanced with specialized tools for coverage analysis and mocking, ensures our code is reliable, maintainable, and performs as expected across all levels of the application.
