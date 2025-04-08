import unittest
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forestfire.optimizer.utils.geometry import WalkwayCalculator

class TestWalkwayCalculator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.left_walkway = 15
        self.right_walkway = 105
        self.calculator = WalkwayCalculator(self.left_walkway, self.right_walkway)
    
    def test_get_walkway_position_left(self):
        """Test getting left walkway position"""
        # Values divisible by 20 should return left walkway
        self.assertEqual(self.calculator.get_walkway_position(0), self.left_walkway)
        self.assertEqual(self.calculator.get_walkway_position(20), self.left_walkway)
        self.assertEqual(self.calculator.get_walkway_position(40), self.left_walkway)
        self.assertEqual(self.calculator.get_walkway_position(100), self.left_walkway)
    
    def test_get_walkway_position_right(self):
        """Test getting right walkway position"""
        # Values not divisible by 20 should return right walkway
        self.assertEqual(self.calculator.get_walkway_position(1), self.right_walkway)
        self.assertEqual(self.calculator.get_walkway_position(19), self.right_walkway)
        self.assertEqual(self.calculator.get_walkway_position(21), self.right_walkway)
        self.assertEqual(self.calculator.get_walkway_position(99), self.right_walkway)
    
    def test_custom_walkway_values(self):
        """Test with custom walkway values"""
        custom_calculator = WalkwayCalculator(10, 90)
        
        # Check with custom values
        self.assertEqual(custom_calculator.get_walkway_position(0), 10)
        self.assertEqual(custom_calculator.get_walkway_position(1), 90)

if __name__ == '__main__':
    unittest.main()
