import unittest
import sys
import os
from unittest.mock import MagicMock, patch
import random
import numpy as np

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forestfire.algorithms.genetic import GeneticOperator
from forestfire.utils.config import NUM_PICKERS, PICKER_CAPACITIES, PC

class TestGeneticOperator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.route_optimizer = MagicMock()
        self.genetic_op = GeneticOperator(self.route_optimizer)
        # Set fixed seed for reproducibility
        random.seed(42)
        np.random.seed(42)
    
    def test_tournament_selection(self):
        """Test tournament selection picks the best solution"""
        # Create a population with known fitness values
        pop = [
            [[0, 1, 2, 0], 100],  # Worse fitness
            [[1, 0, 1, 2], 50],   # Better fitness
            [[2, 2, 0, 1], 75]    # Medium fitness
        ]
        
        # Mock random.sample to always return the first and second solutions
        with patch('random.sample', return_value=[pop[0], pop[1]]):
            selected = self.genetic_op.tournament_selection(pop, 2)
            
            # Should select the solution with better fitness (lower value)
            self.assertEqual(selected, [1, 0, 1, 2])
    
    def test_single_point_crossover(self):
        """Test single point crossover creates valid offspring"""
        parent1 = [0, 1, 2, 0, 1]
        parent2 = [2, 2, 1, 0, 0]
        
        # Mock random.randint to return a fixed crossover point
        with patch('random.randint', return_value=2):
            offspring1, offspring2 = self.genetic_op._single_point_crossover(parent1, parent2)
            
            # Check crossover results
            self.assertEqual(offspring1, [0, 1, 1, 0, 0])
            self.assertEqual(offspring2, [2, 2, 2, 0, 1])
    
    def test_uniform_crossover(self):
        """Test uniform crossover creates valid offspring"""
        parent1 = [0, 1, 2, 0, 1]
        parent2 = [2, 2, 1, 0, 0]
        
        # Mock random.random to alternate between parents
        with patch('random.random', side_effect=[0.3, 0.7, 0.3, 0.7, 0.3]):
            offspring1, offspring2 = self.genetic_op._uniform_crossover(parent1, parent2)
            
            # With our mocked values, offspring1 should take from parent1 when random < 0.5
            # and offspring2 should take from parent2 when random < 0.5
            self.assertEqual(offspring1, [0, 2, 2, 0, 1])
            self.assertEqual(offspring2, [2, 1, 1, 0, 0])
    
    def test_crossover_probability(self):
        """Test crossover respects probability threshold"""
        parent1 = [0, 1, 2, 0, 1]
        parent2 = [2, 2, 1, 0, 0]
        
        # Test when q > PC (no crossover)
        with patch('random.uniform', return_value=0.95):  # PC is 0.90
            offspring1, offspring2 = self.genetic_op.crossover(parent1, parent2)
            
            # Should return parents unchanged
            self.assertEqual(offspring1, parent1)
            self.assertEqual(offspring2, parent2)
        
        # Test when q <= PC (perform crossover)
        with patch('random.uniform', return_value=0.5):
            with patch('random.randint', return_value=1):  # Choose single-point
                with patch('random.randint', return_value=2):  # Crossover point
                    offspring1, offspring2 = self.genetic_op.crossover(parent1, parent2)
                    
                    # Should perform crossover
                    self.assertNotEqual(offspring1, parent1)
                    self.assertNotEqual(offspring2, parent2)
    
    def test_mutate_with_capacity(self):
        """Test mutation respects picker capacity constraints"""
        # Create a solution where each picker is at capacity
        solution = [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]
        picker_capacities = [4, 3, 3]  # Each picker is at capacity
        
        # Mock np.random.randint to try changing index 0 from picker 0 to picker 1
        with patch('numpy.random.randint', side_effect=[0, 1]):
            # This should fail capacity check and return original solution
            mutated = self.genetic_op.mutate_with_capacity(solution, picker_capacities)
            self.assertEqual(mutated, solution)
        
        # Create a solution where picker 1 has room for one more
        solution = [0, 1, 2, 0, 1, 2, 0, 0, 2, 0]
        picker_capacities = [4, 3, 3]  # Picker 1 has room for one more
        
        # Mock np.random.randint to change index 7 from picker 0 to picker 1
        with patch('numpy.random.randint', side_effect=[7, 1]):
            # This should succeed and return mutated solution
            mutated = self.genetic_op.mutate_with_capacity(solution, picker_capacities)
            expected = [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]
            self.assertEqual(mutated, expected)
    
    def test_enforce_capacity_constraints(self):
        """Test capacity constraint enforcement"""
        # Create a solution that violates capacity constraints
        solution = [0, 0, 0, 0, 0, 1, 1, 2]  # Picker 0 exceeds capacity
        picker_capacities = [3, 3, 2]
        
        # Enforce constraints
        fixed_solution = self.genetic_op._enforce_capacity_constraints(solution, picker_capacities)
        
        # Count assignments after fixing
        counts = [fixed_solution.count(i) for i in range(len(picker_capacities))]
        
        # Check that capacities are respected
        for picker_id, count in enumerate(counts):
            self.assertLessEqual(count, picker_capacities[picker_id])

if __name__ == '__main__':
    unittest.main()
