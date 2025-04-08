import unittest
import sys
import os
from unittest.mock import MagicMock, patch
import numpy as np

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forestfire.optimizer.fitness import calc_distance_with_shortest_route
from forestfire.optimizer.utils import e_d, walkway_from_condition
from forestfire.utils.config import NUM_PICKERS

class TestFitness(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        # Sample data for testing
        self.picker_locations = [(0, 0), (10, 10), (20, 20)]
        self.emptypop_position = [0, 1, 2]  # Each order assigned to a different picker
        self.orders_assign = [
            [(5, 5)],    # Order 0 location
            [(15, 15)],  # Order 1 location
            [(25, 25)]   # Order 2 location
        ]
        self.picktasks = ["task1", "task2", "task3"]
        self.stage_result = {
            "task1": [(30, 30)],
            "task2": [(35, 35)],
            "task3": [(40, 40)]
        }

    @patch('forestfire.optimizer.utils.e_d', return_value=10.0)
    @patch('forestfire.optimizer.utils.walkway_from_condition')
    def test_calc_distance_with_shortest_route(self, mock_walkway, mock_distance):
        """Test the main fitness calculation function"""
        # Configure the walkway mock to return consistent values
        mock_walkway.side_effect = lambda val, left, right: 15 if val % 20 == 0 else 105

        # Call the function
        total_cost, routes, assignments = calc_distance_with_shortest_route(
            self.picker_locations,
            self.emptypop_position,
            self.orders_assign,
            self.picktasks,
            self.stage_result
        )

        # Check that the function returns expected types
        self.assertIsInstance(total_cost, (int, float))
        self.assertIsInstance(routes, list)
        self.assertIsInstance(assignments, list)

        # Check that routes and assignments have the correct length
        self.assertEqual(len(routes), NUM_PICKERS)
        self.assertEqual(len(assignments), NUM_PICKERS)

        # Check that the distance calculator was called
        self.assertGreater(mock_distance.call_count, 0)

        # Check that the walkway calculator was called
        self.assertGreater(mock_walkway.call_count, 0)

    @patch('forestfire.optimizer.utils.e_d', return_value=10.0)
    @patch('forestfire.optimizer.utils.walkway_from_condition')
    def test_calc_distance_with_empty_orders(self, mock_walkway, mock_distance):
        """Test fitness calculation with empty orders"""
        # Configure the walkway mock to return consistent values
        mock_walkway.side_effect = lambda val, left, right: 15 if val % 20 == 0 else 105

        # Empty orders
        emptypop_position = []
        orders_assign = []
        picktasks = []

        # Call the function
        total_cost, routes, assignments = calc_distance_with_shortest_route(
            self.picker_locations,
            emptypop_position,
            orders_assign,
            picktasks,
            self.stage_result
        )

        # Check that the function handles empty input gracefully
        self.assertEqual(total_cost, 0)
        self.assertEqual(len(routes), NUM_PICKERS)
        self.assertEqual(len(assignments), NUM_PICKERS)

    @patch('forestfire.optimizer.utils.e_d')
    @patch('forestfire.optimizer.utils.walkway_from_condition')
    def test_calc_distance_with_multiple_orders_per_picker(self, mock_walkway, mock_distance):
        """Test fitness calculation with multiple orders per picker"""
        # Configure the walkway mock to return consistent values
        mock_walkway.side_effect = lambda val, left, right: 15 if val % 20 == 0 else 105

        # Configure the distance mock to return different values based on points
        mock_distance.side_effect = lambda p1, p2: ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

        # Multiple orders per picker
        emptypop_position = [0, 0, 1, 1, 2, 2]
        orders_assign = [
            [(5, 5)],    # Order 0 location
            [(6, 6)],    # Order 1 location
            [(15, 15)],  # Order 2 location
            [(16, 16)],  # Order 3 location
            [(25, 25)],  # Order 4 location
            [(26, 26)]   # Order 5 location
        ]
        picktasks = ["task1", "task2", "task3", "task4", "task5", "task6"]

        # Call the function
        total_cost, routes, assignments = calc_distance_with_shortest_route(
            self.picker_locations,
            emptypop_position,
            orders_assign,
            picktasks,
            self.stage_result
        )

        # Check that the function returns expected types
        self.assertIsInstance(total_cost, (int, float))
        self.assertIsInstance(routes, list)
        self.assertIsInstance(assignments, list)

        # Check that routes and assignments have the correct length
        self.assertEqual(len(routes), NUM_PICKERS)
        self.assertEqual(len(assignments), NUM_PICKERS)

        # Check that assignments are correctly grouped by picker
        self.assertEqual(len(assignments[0]), 2)  # Picker 0 has 2 orders
        self.assertEqual(len(assignments[1]), 2)  # Picker 1 has 2 orders
        self.assertEqual(len(assignments[2]), 2)  # Picker 2 has 2 orders

if __name__ == '__main__':
    unittest.main()
