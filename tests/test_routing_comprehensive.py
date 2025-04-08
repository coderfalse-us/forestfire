import unittest
import sys
import os
from unittest.mock import MagicMock, patch
import numpy as np

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forestfire.optimizer.services.routing import RouteOptimizer
from forestfire.optimizer.models.route import Route
from forestfire.utils.config import NUM_PICKERS

class TestRouteOptimizerComprehensive(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.route_optimizer = RouteOptimizer(
            left_walkway=15,
            right_walkway=105,
            step_between_rows=10
        )
        
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
    
    def test_get_staging_points(self):
        """Test getting staging points"""
        # Mock data
        order_indices = [[0], [1], [2]]  # Each picker has one order
        
        # Call the method
        staging_points = self.route_optimizer._get_staging_points(
            order_indices, 
            self.picktasks, 
            self.stage_result
        )
        
        # Check that staging points are returned
        self.assertIsInstance(staging_points, list)
    
    def test_handle_entry_logic(self):
        """Test entry logic handling"""
        # Mock data
        picker_location = (0, 0)
        route = [(5, 5), (10, 10)]
        picker_id = 0
        r_flag = [0, 0, 0]
        
        # Call the method
        result = self.route_optimizer._handle_entry_logic(
            picker_location, 
            route, 
            picker_id, 
            r_flag
        )
        
        # Check that a route is returned
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), len(route))
    
    def test_handle_serpentine_logic(self):
        """Test serpentine logic handling"""
        # Mock data
        sorted_data = [
            [(5, 5), (10, 10)],  # Picker 0 route
            [(15, 15), (20, 20)],  # Picker 1 route
            [(25, 25), (30, 30)]   # Picker 2 route
        ]
        r_flag = [0, 1, 0]  # Different flags for different pickers
        final_result = [(40, 40)]  # Staging point
        
        # Call the method
        result = self.route_optimizer._handle_serpentine_logic(
            sorted_data, 
            r_flag, 
            final_result
        )
        
        # Check that routes are returned
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(sorted_data))
        
        # Check that each route includes the staging point
        for route in result:
            if route:  # Skip empty routes
                self.assertIn((40, 40), route)
    
    def test_handle_aisle_transition(self):
        """Test aisle transition handling"""
        # Mock data
        route = [(5, 5), (10, 10), (15, 15)]
        index = 0
        r_flag = 0
        
        # Call the method
        result = self.route_optimizer._handle_aisle_transition(
            route, 
            index, 
            r_flag
        )
        
        # Check that an index is returned
        self.assertIsInstance(result, int)
    
    def test_ensure_point_tuple_with_list(self):
        """Test point tuple conversion with list input"""
        # Test with list
        point = [10, 20]
        result = self.route_optimizer._ensure_point_tuple(point)
        
        # Check that a tuple is returned
        self.assertIsInstance(result, tuple)
        self.assertEqual(result, (10, 20))
    
    def test_ensure_point_tuple_with_tuple(self):
        """Test point tuple conversion with tuple input"""
        # Test with tuple
        point = (10, 20)
        result = self.route_optimizer._ensure_point_tuple(point)
        
        # Check that the same tuple is returned
        self.assertIsInstance(result, tuple)
        self.assertEqual(result, point)
    
    def test_ensure_point_tuple_with_invalid_input(self):
        """Test point tuple conversion with invalid input"""
        # Test with invalid input
        with self.assertRaises(TypeError):
            self.route_optimizer._ensure_point_tuple("invalid")
    
    @patch('forestfire.optimizer.services.routing.RouteOptimizer._get_staging_points')
    @patch('forestfire.optimizer.services.routing.RouteOptimizer._sort_locations')
    @patch('forestfire.optimizer.services.routing.RouteOptimizer._handle_entry_logic')
    @patch('forestfire.optimizer.services.routing.RouteOptimizer._handle_serpentine_logic')
    @patch('forestfire.optimizer.services.routing.RouteOptimizer._calculate_route_cost')
    def test_calculate_shortest_route_comprehensive(
        self, 
        mock_calculate_cost, 
        mock_serpentine, 
        mock_entry, 
        mock_sort, 
        mock_staging
    ):
        """Test the entire shortest route calculation process"""
        # Configure mocks
        mock_staging.return_value = [(40, 40)]
        mock_sort.return_value = [
            [(5, 5)],    # Picker 0 sorted locations
            [(15, 15)],  # Picker 1 sorted locations
            [(25, 25)]   # Picker 2 sorted locations
        ]
        mock_entry.side_effect = lambda loc, route, idx, flag: route
        mock_serpentine.return_value = [
            [(5, 5), (40, 40)],    # Picker 0 optimized route
            [(15, 15), (40, 40)],  # Picker 1 optimized route
            [(25, 25), (40, 40)]   # Picker 2 optimized route
        ]
        mock_calculate_cost.side_effect = [10.0, 20.0, 30.0]  # Different costs for each route
        
        # Call the method
        total_cost, routes, assignments = self.route_optimizer.calculate_shortest_route(
            self.picker_locations,
            self.emptypop_position,
            self.orders_assign,
            self.picktasks,
            self.stage_result
        )
        
        # Check that the function returns expected values
        self.assertEqual(total_cost, 60.0)  # Sum of all route costs
        self.assertEqual(len(routes), NUM_PICKERS)
        self.assertEqual(len(assignments), NUM_PICKERS)
        
        # Check that each route has the correct properties
        for i, route in enumerate(routes):
            self.assertEqual(route.picker_id, i)
            self.assertEqual(route.cost, [10.0, 20.0, 30.0][i])
            self.assertEqual(route.assigned_orders, [i])
        
        # Check that all mocks were called
        mock_staging.assert_called_once()
        mock_sort.assert_called_once()
        self.assertEqual(mock_entry.call_count, NUM_PICKERS)
        mock_serpentine.assert_called_once()
        self.assertEqual(mock_calculate_cost.call_count, NUM_PICKERS)

if __name__ == '__main__':
    unittest.main()
