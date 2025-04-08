import unittest
import sys
import os
import math

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forestfire.optimizer.services.distance import DistanceCalculator

class TestDistanceCalculator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.distance_calculator = DistanceCalculator()
    
    def test_euclidean_distance_integer_points(self):
        """Test Euclidean distance calculation with integer points"""
        point1 = (0, 0)
        point2 = (3, 4)
        
        distance = self.distance_calculator.euclidean_distance(point1, point2)
        
        # Expected distance is 5.0 (Pythagorean theorem: sqrt(3^2 + 4^2))
        self.assertEqual(distance, 5.0)
    
    def test_euclidean_distance_float_points(self):
        """Test Euclidean distance calculation with float points"""
        point1 = (1.5, 2.5)
        point2 = (4.5, 6.5)
        
        distance = self.distance_calculator.euclidean_distance(point1, point2)
        
        # Expected distance is 5.0 (sqrt((4.5-1.5)^2 + (6.5-2.5)^2))
        expected = math.sqrt((4.5-1.5)**2 + (6.5-2.5)**2)
        self.assertAlmostEqual(distance, expected)
    
    def test_euclidean_distance_same_point(self):
        """Test Euclidean distance calculation with identical points"""
        point = (10, 20)
        
        distance = self.distance_calculator.euclidean_distance(point, point)
        
        # Distance between same points should be 0
        self.assertEqual(distance, 0.0)
    
    def test_euclidean_distance_negative_coordinates(self):
        """Test Euclidean distance calculation with negative coordinates"""
        point1 = (-3, -4)
        point2 = (0, 0)
        
        distance = self.distance_calculator.euclidean_distance(point1, point2)
        
        # Expected distance is 5.0
        self.assertEqual(distance, 5.0)
    
    def test_euclidean_distance_string_coordinates(self):
        """Test Euclidean distance calculation with string coordinates"""
        point1 = ("3", "4")
        point2 = ("0", "0")
        
        distance = self.distance_calculator.euclidean_distance(point1, point2)
        
        # Should convert strings to floats and calculate correctly
        self.assertEqual(distance, 5.0)
    
    def test_euclidean_distance_invalid_input(self):
        """Test Euclidean distance calculation with invalid input"""
        point1 = (0, 0)
        point2 = "invalid"
        
        # Should raise TypeError
        with self.assertRaises(TypeError):
            self.distance_calculator.euclidean_distance(point1, point2)
        
        point1 = (0, "invalid")
        point2 = (0, 0)
        
        # Should raise TypeError or ValueError
        with self.assertRaises((TypeError, ValueError)):
            self.distance_calculator.euclidean_distance(point1, point2)

if __name__ == '__main__':
    unittest.main()
