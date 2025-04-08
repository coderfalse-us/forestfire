import unittest
import sys
import os
from unittest.mock import patch
import random

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import initialize_population
from forestfire.utils.config import NUM_PICKERS, N_POP

class TestInitialization(unittest.TestCase):
    
    def test_initialize_population_size(self):
        """Test that initialize_population returns the correct number of assignments"""
        num_pickers = 5
        orders_size = 20
        picker_capacities = [5] * num_pickers
        
        population = initialize_population(num_pickers, orders_size, picker_capacities)
        
        # Check if population size is correct (N_POP - 1)
        self.assertEqual(len(population), N_POP - 1)
        
        # Check if each assignment has the correct length
        for assignment in population:
            self.assertEqual(len(assignment), orders_size)
    
    def test_initialize_population_valid_assignments(self):
        """Test that initialize_population creates valid picker assignments"""
        num_pickers = 3
        orders_size = 15
        picker_capacities = [5, 6, 4]  # Different capacities for each picker
        
        # Set a fixed seed for reproducibility
        random.seed(42)
        population = initialize_population(num_pickers, orders_size, picker_capacities)
        
        # Check if assignments respect picker capacities
        for assignment in population:
            # Count assignments per picker
            picker_counts = [0] * num_pickers
            for picker_id in assignment:
                picker_counts[picker_id] += 1
                
            # Verify counts don't exceed capacities
            for picker_id, count in enumerate(picker_counts):
                self.assertLessEqual(count, picker_capacities[picker_id],
                                    f"Picker {picker_id} exceeded capacity: {count} > {picker_capacities[picker_id]}")
    
    def test_initialize_population_picker_range(self):
        """Test that initialize_population only assigns valid picker IDs"""
        num_pickers = 4
        orders_size = 10
        picker_capacities = [3] * num_pickers
        
        population = initialize_population(num_pickers, orders_size, picker_capacities)
        
        # Check if all picker IDs are within valid range
        for assignment in population:
            for picker_id in assignment:
                self.assertGreaterEqual(picker_id, 0)
                self.assertLess(picker_id, num_pickers)
    
    @patch('random.choice')
    def test_initialize_population_random_choice(self, mock_choice):
        """Test that initialize_population uses random.choice for assignments"""
        num_pickers = 2
        orders_size = 5
        picker_capacities = [3, 2]
        
        # Configure mock to return alternating picker IDs
        mock_choice.side_effect = [0, 1, 0, 1, 0]
        
        population = initialize_population(num_pickers, orders_size, picker_capacities)
        
        # Verify random.choice was called the expected number of times
        self.assertEqual(mock_choice.call_count, orders_size)
        
        # Check the first assignment matches our mocked values
        expected_assignment = [0, 1, 0, 1, 0]
        # Note: The assignment might be shuffled, so we can't directly compare
        # Instead, we check that the counts match
        self.assertEqual(population[0].count(0), expected_assignment.count(0))
        self.assertEqual(population[0].count(1), expected_assignment.count(1))

if __name__ == '__main__':
    unittest.main()
