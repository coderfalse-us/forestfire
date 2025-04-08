import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forestfire.database.services.picklist import PicklistRepository
from forestfire.database.services.batch_pick_seq_service import BatchPickSequenceService
from forestfire.database.exceptions import QueryError

class TestPicklistRepository(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock for BaseRepository
        self.mock_base_repo = MagicMock()
        
        # Patch the BaseRepository to return our mock
        with patch('forestfire.database.services.picklist.BaseRepository', return_value=self.mock_base_repo):
            self.picklist_repo = PicklistRepository()
    
    def test_fetch_picklist_data(self):
        """Test fetching picklist data"""
        # Mock data to be returned by execute_query
        mock_data = [
            (1, 'task1', 'location1', 'batch1'),
            (2, 'task2', 'location2', 'batch2')
        ]
        self.mock_base_repo.execute_query.return_value = mock_data
        
        # Call the method
        result = self.picklist_repo.fetch_picklist_data()
        
        # Check that execute_query was called with correct parameters
        self.mock_base_repo.execute_query.assert_called_once()
        
        # Check that the result matches our mock data
        self.assertEqual(result, mock_data)
    
    def test_fetch_picklist_data_error(self):
        """Test error handling when fetching picklist data"""
        # Mock execute_query to raise an exception
        self.mock_base_repo.execute_query.side_effect = Exception("Database error")
        
        # Call the method and check that it raises QueryError
        with self.assertRaises(QueryError):
            self.picklist_repo.fetch_picklist_data()
    
    def test_fetch_distinct_picktasks(self):
        """Test fetching distinct picktasks"""
        # Mock data to be returned by execute_query
        mock_data = [('task1',), ('task2',), ('task3',)]
        self.mock_base_repo.execute_query.return_value = mock_data
        
        # Call the method
        result = self.picklist_repo.fetch_distinct_picktasks()
        
        # Check that execute_query was called
        self.mock_base_repo.execute_query.assert_called_once()
        
        # Check that the result is correctly extracted
        self.assertEqual(result, ['task1', 'task2', 'task3'])
    
    def test_update_batchid(self):
        """Test updating batch ID"""
        # Call the method
        self.picklist_repo.update_batchid('batch123', 'task456')
        
        # Check that execute_query was called with correct parameters
        self.mock_base_repo.execute_query.assert_called_once()
        
        # Check that the query contains the batch ID and picktask ID
        call_args = self.mock_base_repo.execute_query.call_args[0][0]
        self.assertIn("batch123", call_args)
        self.assertIn("task456", call_args)
    
    @patch('forestfire.database.services.picklist.PicklistRepository.map_picklist_data')
    def test_get_optimized_data(self, mock_map_picklist_data):
        """Test getting optimized data"""
        # Mock data to be returned by map_picklist_data
        mock_staging = {'task1': [(10, 10)], 'task2': [(20, 20)]}
        mock_taskid = {'task1': [(1, 1)], 'task2': [(2, 2)]}
        mock_id_mapping = {'task1': 101, 'task2': 102}
        mock_map_picklist_data.return_value = (mock_staging, mock_taskid, mock_id_mapping)
        
        # Call the method
        task_keys, locations, staging, picklistids = self.picklist_repo.get_optimized_data()
        
        # Check that map_picklist_data was called
        mock_map_picklist_data.assert_called_once()
        
        # Check the results
        self.assertEqual(task_keys, ['task1', 'task2'])
        self.assertEqual(locations, [[(1, 1)], [(2, 2)]])
        self.assertEqual(staging, mock_staging)
        self.assertEqual(picklistids, [101, 102])


class TestBatchPickSequenceService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mocks
        self.mock_picklist_repo = MagicMock()
        self.mock_route_optimizer = MagicMock()
        
        # Patch the dependencies
        with patch('forestfire.database.services.batch_pick_seq_service.PicklistRepository', 
                  return_value=self.mock_picklist_repo):
            with patch('forestfire.database.services.batch_pick_seq_service.RouteOptimizer', 
                      return_value=self.mock_route_optimizer):
                self.batch_service = BatchPickSequenceService()
    
    def test_update_pick_sequences(self):
        """Test updating pick sequences"""
        # Mock data
        final_solution = [0, 1, 0]  # Orders 0 and 2 to picker 0, order 1 to picker 1
        picklistids = [101, 102, 103]
        orders_assign = [[(5, 5)], [(15, 15)], [(25, 25)]]
        picktasks = ["task1", "task2", "task3"]
        stage_result = {"task1": [(30, 30)], "task2": [(35, 35)], "task3": [(40, 40)]}
        
        # Mock route_optimizer.calculate_shortest_route
        mock_routes = [
            MagicMock(picker_id=0, locations=[(5, 5), (25, 25)], assigned_orders=[0, 2]),
            MagicMock(picker_id=1, locations=[(15, 15)], assigned_orders=[1])
        ]
        self.mock_route_optimizer.calculate_shortest_route.return_value = (100, mock_routes, [])
        
        # Call the method
        self.batch_service.update_pick_sequences(
            final_solution, picklistids, orders_assign, picktasks, stage_result
        )
        
        # Check that calculate_shortest_route was called
        self.mock_route_optimizer.calculate_shortest_route.assert_called_once()
        
        # Check that execute_transaction was called
        self.mock_picklist_repo.baserepository.execute_transaction.assert_called_once()
        
        # Check that the transaction contains updates for each route
        transaction = self.mock_picklist_repo.baserepository.execute_transaction.call_args[0][0]
        self.assertGreater(len(transaction), 0)

if __name__ == '__main__':
    unittest.main()
