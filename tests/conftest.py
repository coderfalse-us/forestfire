import pytest
import sys
import os
from unittest.mock import patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the config override module first
from tests import test_config_override

@pytest.fixture(autouse=True)
def mock_database_connection():
    """Mock database connection for all tests"""
    with patch('forestfire.database.connection.DatabaseConnectionManager.get_connection'):
        yield

@pytest.fixture
def sample_picker_locations():
    """Sample picker locations for testing"""
    return [(0, 0), (10, 10), (20, 20), (30, 30)]

@pytest.fixture
def sample_orders_assign():
    """Sample order assignments for testing"""
    return [
        [(5, 5)],    # Order 0 location
        [(15, 15)],  # Order 1 location
        [(25, 25)],  # Order 2 location
        [(35, 35)]   # Order 3 location
    ]

@pytest.fixture
def sample_picktasks():
    """Sample picktask IDs for testing"""
    return ["task1", "task2", "task3", "task4"]

@pytest.fixture
def sample_stage_result():
    """Sample staging locations for testing"""
    return {
        "task1": [(40, 40)],
        "task2": [(45, 45)],
        "task3": [(50, 50)],
        "task4": [(55, 55)]
    }

@pytest.fixture
def sample_emptypop_position():
    """Sample picker assignments for testing"""
    return [0, 1, 2, 3]  # Each order assigned to a different picker

@pytest.fixture
def sample_picker_capacities():
    """Sample picker capacities for testing"""
    return [2, 2, 2, 2]
