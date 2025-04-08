import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import main
from forestfire.utils.config import NUM_PICKERS, PICKER_CAPACITIES, NUM_ANTS, MAX_IT

class TestMain(unittest.TestCase):
    
    @patch('main.PicklistRepository')
    @patch('main.RouteOptimizer')
    @patch('main.GeneticOperator')
    @patch('main.AntColonyOptimizer')
    @patch('main.PathVisualizer')
    @patch('main.BatchPickSequenceService')
    @patch('main.initialize_population')
    def test_main_function(self, mock_init_pop, mock_batch_service, mock_visualizer, 
                          mock_aco, mock_genetic, mock_route_optimizer, mock_picklist_repo):
        """Test the main function execution flow"""
        # Mock repository data
        mock_picklist_instance = mock_picklist_repo.return_value
        mock_picklist_instance.get_optimized_data.return_value = (
            ["task1", "task2"],  # picktasks
            [[(5, 5)], [(15, 15)]],  # orders_assign
            {"task1": [(30, 30)], "task2": [(35, 35)]},  # stage_result
            [101, 102]  # picklistids
        )
        
        # Mock route optimizer
        mock_route_optimizer_instance = mock_route_optimizer.return_value
        mock_route_optimizer_instance.calculate_shortest_route.return_value = (
            100.0,  # fitness_score
            [MagicMock()],  # routes
            []  # assignments
        )
        
        # Mock genetic operator
        mock_genetic_instance = mock_genetic.return_value
        mock_genetic_instance.tournament_selection.return_value = [0, 1]
        mock_genetic_instance.crossover.return_value = ([0, 1], [1, 0])
        mock_genetic_instance.mutate_with_capacity.return_value = [0, 1]
        
        # Mock ACO
        mock_aco_instance = mock_aco.return_value
        mock_aco_instance.calculate_heuristic.return_value = MagicMock()
        mock_aco_instance.build_solution.return_value = [0, 1]
        
        # Mock initial population
        mock_init_pop.return_value = [[0, 1], [1, 0]]
        
        # Call main function
        main.main()
        
        # Verify service initialization
        mock_picklist_repo.assert_called_once()
        mock_route_optimizer.assert_called_once()
        mock_genetic.assert_called_once()
        mock_aco.assert_called_once()
        mock_visualizer.assert_called_once()
        mock_batch_service.assert_called_once()
        
        # Verify data retrieval
        mock_picklist_instance.get_optimized_data.assert_called_once()
        
        # Verify population initialization
        mock_init_pop.assert_called_once_with(NUM_PICKERS, 2, PICKER_CAPACITIES)
        
        # Verify ACO execution
        mock_aco_instance.calculate_heuristic.assert_called_once()
        self.assertEqual(mock_aco_instance.build_solution.call_count, NUM_ANTS)
        
        # Verify genetic algorithm execution
        self.assertGreaterEqual(mock_genetic_instance.tournament_selection.call_count, 1)
        self.assertGreaterEqual(mock_genetic_instance.crossover.call_count, 1)
        self.assertGreaterEqual(mock_genetic_instance.mutate_with_capacity.call_count, 1)
        
        # Verify visualization and database updates
        mock_visualizer_instance = mock_visualizer.return_value
        mock_visualizer_instance.plot_routes.assert_called_once()
        
        mock_batch_service_instance = mock_batch_service.return_value
        mock_batch_service_instance.update_pick_sequences.assert_called_once()
    
    @patch('main.logging.basicConfig')
    @patch('main.main')
    def test_main_script_execution(self, mock_main, mock_logging_config):
        """Test script execution when run as __main__"""
        # Save the original __name__
        original_name = main.__name__
        
        try:
            # Set __name__ to "__main__"
            main.__name__ = "__main__"
            
            # Re-execute the module
            exec(open(os.path.join(os.path.dirname(__file__), '..', 'main.py')).read())
            
            # Check that logging was configured
            mock_logging_config.assert_called_once()
            
            # Check that main was called
            mock_main.assert_called_once()
            
        finally:
            # Restore the original __name__
            main.__name__ = original_name

if __name__ == '__main__':
    unittest.main()
