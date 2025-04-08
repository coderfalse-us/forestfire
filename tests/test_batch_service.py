import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forestfire.database.services.batch_service import BatchService

class TestBatchService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock for PicklistRepository
        self.mock_picklist_repo = MagicMock()
        
        # Patch the PicklistRepository to return our mock
        with patch('forestfire.database.services.batch_service.PicklistRepository', 
                  return_value=self.mock_picklist_repo):
            self.batch_service = BatchService()
    
    def test_update_batch_assignments(self):
        """Test updating batch assignments"""
        # Mock data
        final_solution = [0, 1, 0]  # Orders 0 and 2 to picker 0, order 1 to picker 1
        picklistids = [101, 102, 103]
        
        # Call the method
        self.batch_service.update_batch_assignments(final_solution, picklistids)
        
        # Check that execute_transaction was called
        self.mock_picklist_repo.baserepository.execute_transaction.assert_called_once()
        
        # Check that the transaction contains updates for each assignment
        transaction = self.mock_picklist_repo.baserepository.execute_transaction.call_args[0][0]
        self.assertEqual(len(transaction), 3)  # 3 updates for 3 assignments
        
        # Check that the batch IDs are correctly formatted
        for i, (query, params) in enumerate(transaction):
            self.assertIn("UPDATE picklist", query)
            self.assertIn("SET batchid", query)
            
            batch_id = params[0]
            picklist_id = params[1]
            
            expected_batch_id = f"BATCH_{final_solution[i]}"
            expected_picklist_id = picklistids[i]
            
            self.assertEqual(batch_id, expected_batch_id)
            self.assertEqual(picklist_id, expected_picklist_id)
    
    def test_update_batch_assignments_empty(self):
        """Test updating batch assignments with empty data"""
        # Empty data
        final_solution = []
        picklistids = []
        
        # Call the method
        self.batch_service.update_batch_assignments(final_solution, picklistids)
        
        # Check that execute_transaction was not called
        self.mock_picklist_repo.baserepository.execute_transaction.assert_not_called()
    
    def test_update_batch_assignments_error(self):
        """Test error handling when updating batch assignments"""
        # Mock data
        final_solution = [0, 1, 0]
        picklistids = [101, 102, 103]
        
        # Mock execute_transaction to raise an exception
        self.mock_picklist_repo.baserepository.execute_transaction.side_effect = Exception("Database error")
        
        # Call the method and check that it handles the exception
        with self.assertRaises(Exception):
            self.batch_service.update_batch_assignments(final_solution, picklistids)
        
        # Check that execute_transaction was called
        self.mock_picklist_repo.baserepository.execute_transaction.assert_called_once()

if __name__ == '__main__':
    unittest.main()
