import unittest
import sys
import os
from unittest.mock import MagicMock, patch
import numpy as np

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.optimizer.models.route import Route

class TestRouteOptimizer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.route_optimizer = RouteOptimizer(
            left_walkway=15,
            right_walkway=105,
            step_between_rows=10
        )
        # Mock the distance calculator
        self.route_optimizer.distance_calculator.euclidean_distance = MagicMock(return_value=10.0)
    
    def test_calculate_route_cost(self):
        """Test route cost calculation"""
        # Create a simple path
        path = [(0, 0), (10, 10), (20, 20)]
        
        # Calculate cost
        cost = self.route_optimizer._calculate_route_cost(path)
        
        # With our mocked distance calculator, each segment should have distance 10.0
        expected_cost = 20.0  # 2 segments * 10.0
        self.assertEqual(cost, expected_cost)
        
        # Check that the distance calculator was called the correct number of times
        self.assertEqual(self.route_optimizer.distance_calculator.euclidean_distance.call_count, 2)
    
    def test_calculate_route_cost_empty_path(self):
        """Test route cost calculation with empty path"""
        # Empty path should have zero cost
        cost = self.route_optimizer._calculate_route_cost([])
        self.assertEqual(cost, 0.0)
        
        # Distance calculator should not be called
        self.route_optimizer.distance_calculator.euclidean_distance.assert_not_called()
    
    def test_ensure_point_tuple(self):
        """Test point tuple conversion"""
        # Test with tuple
        point = (10, 20)
        result = self.route_optimizer._ensure_point_tuple(point)
        self.assertEqual(result, point)
        
        # Test with list
        point = [30, 40]
        result = self.route_optimizer._ensure_point_tuple(point)
        self.assertEqual(result, (30, 40))
        
        # Test with invalid input
        with self.assertRaises(TypeError):
            self.route_optimizer._ensure_point_tuple("invalid")
    
    def test_sort_locations(self):
        """Test location sorting"""
        # Create sample assignments
        assignments = [
            [(10, 30), (20, 30)],  # Picker 0 assignments
            [(50, 40), (40, 40)],  # Picker 1 assignments
            []                      # Picker 2 assignments (empty)
        ]
        
        sorted_data = self.route_optimizer._sort_locations(assignments)
        
        # Check that locations are sorted by y-coordinate
        self.assertEqual(sorted_data[0], [(10, 30), (20, 30)])  # Already sorted
        self.assertEqual(sorted_data[1], [(40, 40), (50, 40)])  # Sorted by x within same y
        self.assertEqual(sorted_data[2], [])                    # Empty remains empty
    
    def test_calculate_shortest_route_simple(self):
        """Test shortest route calculation with simple data"""
        # Mock data
        picker_locations = [(0, 0), (10, 10)]
        emptypop_position = [0, 1, 0]  # Orders 0 and 2 to picker 0, order 1 to picker 1
        orders_assign = [
            [(5, 5)],    # Order 0 location
            [(15, 15)],  # Order 1 location
            [(25, 25)]   # Order 2 location
        ]
        picktasks = ["task1", "task2", "task3"]
        stage_result = {"task1": [(30, 30)], "task2": [(35, 35)], "task3": [(40, 40)]}
        
        # Mock internal methods
        self.route_optimizer._get_staging_points = MagicMock(return_value=[])
        self.route_optimizer._sort_locations = MagicMock(return_value=[
            [(5, 5), (25, 25)],  # Picker 0 sorted locations
            [(15, 15)]           # Picker 1 sorted locations
        ])
        self.route_optimizer._handle_entry_logic = MagicMock(side_effect=lambda loc, route, idx, flag: route)
        self.route_optimizer._handle_serpentine_logic = MagicMock(return_value=[
            [(5, 5), (25, 25)],  # Picker 0 optimized route
            [(15, 15)]           # Picker 1 optimized route
        ])
        
        # Calculate shortest route
        total_cost, routes, assignments = self.route_optimizer.calculate_shortest_route(
            picker_locations, emptypop_position, orders_assign, picktasks, stage_result
        )
        
        # Check results
        self.assertEqual(total_cost, 10.0)  # With our mocked distance calculator
        self.assertEqual(len(routes), 2)
        
        # Check route objects
        self.assertEqual(routes[0].picker_id, 0)
        self.assertEqual(routes[0].locations, [(5, 5), (25, 25)])
        self.assertEqual(routes[0].cost, 10.0)
        self.assertEqual(routes[0].assigned_orders, [0, 2])
        
        self.assertEqual(routes[1].picker_id, 1)
        self.assertEqual(routes[1].locations, [(15, 15)])
        self.assertEqual(routes[1].cost, 0.0)  # Single point has no distance
        self.assertEqual(routes[1].assigned_orders, [1])
        
        # Check assignments
        self.assertEqual(assignments[0], [(5, 5), (25, 25)])
        self.assertEqual(assignments[1], [(15, 15)])

if __name__ == '__main__':
    unittest.main()
