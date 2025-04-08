import unittest
import sys
import os
from unittest.mock import MagicMock, patch
import numpy as np

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forestfire.algorithms.ant_colony import AntColonyOptimizer
from forestfire.utils.config import NUM_PICKERS, ALPHA, BETA, RHO

class TestAntColonyOptimizer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.route_optimizer = MagicMock()
        self.aco = AntColonyOptimizer(self.route_optimizer)
        # Set fixed seed for reproducibility
        np.random.seed(42)
    
    def test_calculate_heuristic(self):
        """Test heuristic calculation"""
        # Mock data
        orders_assign = [
            [(10, 20)],  # Order 1 location
            [(30, 40)],  # Order 2 location
            [(50, 60)]   # Order 3 location
        ]
        
        picker_locations = [
            (5, 5),    # Picker 1 location (close to order 1)
            (35, 45),  # Picker 2 location (close to order 2)
            (60, 70)   # Picker 3 location (close to order 3)
        ]
        
        heuristic = self.aco.calculate_heuristic(orders_assign, picker_locations)
        
        # Check shape of heuristic matrix
        self.assertEqual(heuristic.shape, (len(orders_assign), len(picker_locations)))
        
        # Check that closer pickers have higher heuristic values
        # Order 1 should have highest heuristic for Picker 1
        self.assertGreater(heuristic[0][0], heuristic[0][1])
        self.assertGreater(heuristic[0][0], heuristic[0][2])
        
        # Order 2 should have highest heuristic for Picker 2
        self.assertGreater(heuristic[1][1], heuristic[1][0])
        self.assertGreater(heuristic[1][1], heuristic[1][2])
        
        # Order 3 should have highest heuristic for Picker 3
        self.assertGreater(heuristic[2][2], heuristic[2][0])
        self.assertGreater(heuristic[2][2], heuristic[2][1])
    
    def test_build_solution(self):
        """Test solution building with ACO"""
        orders_size = 5
        pheromone = np.ones((orders_size, NUM_PICKERS))
        heuristic = np.ones((orders_size, NUM_PICKERS))
        picker_capacities = [2] * NUM_PICKERS
        
        # Make some pickers more attractive for certain orders
        for i in range(orders_size):
            preferred_picker = i % NUM_PICKERS
            pheromone[i][preferred_picker] = 2.0
            heuristic[i][preferred_picker] = 2.0
        
        # Build solution
        with patch('numpy.random.choice', side_effect=[0, 1, 2, 3, 4]):
            assignment = self.aco.build_solution(pheromone, heuristic, orders_size, picker_capacities)
            
            # Check assignment length
            self.assertEqual(len(assignment), orders_size)
            
            # Check that all assignments are valid picker IDs
            for picker_id in assignment:
                self.assertGreaterEqual(picker_id, 0)
                self.assertLess(picker_id, NUM_PICKERS)
            
            # Check capacity constraints
            picker_counts = [0] * NUM_PICKERS
            for picker_id in assignment:
                picker_counts[picker_id] += 1
            
            for picker_id, count in enumerate(picker_counts):
                self.assertLessEqual(count, picker_capacities[picker_id])
    
    def test_update_pheromone(self):
        """Test pheromone update mechanism"""
        orders_size = 3
        pheromone = np.ones((orders_size, NUM_PICKERS))
        assignment = [0, 1, 2]  # Each order assigned to a different picker
        fitness_score = 100.0
        
        # Initial pheromone values
        initial_pheromone = pheromone.copy()
        
        # Update pheromone
        self.aco.update_pheromone(pheromone, assignment, fitness_score, orders_size)
        
        # Check that pheromone was updated correctly
        for i in range(orders_size):
            picker_id = assignment[i]
            
            # Pheromone should be updated for assigned pickers
            expected_value = initial_pheromone[i][picker_id] * (1 - RHO) + (1 / fitness_score)
            self.assertAlmostEqual(pheromone[i][picker_id], expected_value)
            
            # Pheromone should remain unchanged for unassigned pickers
            for j in range(NUM_PICKERS):
                if j != picker_id:
                    self.assertEqual(pheromone[i][j], initial_pheromone[i][j])
    
    def test_build_solution_with_full_pickers(self):
        """Test solution building when some pickers are at capacity"""
        orders_size = 6
        pheromone = np.ones((orders_size, NUM_PICKERS))
        heuristic = np.ones((orders_size, NUM_PICKERS))
        
        # Set very limited capacity
        picker_capacities = [1, 2, 3]
        
        # Build solution
        assignment = self.aco.build_solution(pheromone, heuristic, orders_size, picker_capacities)
        
        # Check assignment length
        self.assertEqual(len(assignment), orders_size)
        
        # Count assignments per picker
        picker_counts = [0] * NUM_PICKERS
        for picker_id in assignment:
            if picker_id != -1:  # Skip unassigned orders
                picker_counts[picker_id] += 1
        
        # Check capacity constraints
        for picker_id, count in enumerate(picker_counts):
            self.assertLessEqual(count, picker_capacities[picker_id])

if __name__ == '__main__':
    unittest.main()
