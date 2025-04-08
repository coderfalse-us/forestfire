import unittest
import sys
import os
from unittest.mock import MagicMock, patch
import psycopg2

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forestfire.database.repository import BaseRepository
from forestfire.database.exceptions import QueryError

class TestBaseRepositoryComprehensive(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.repository = BaseRepository()
        
        # Create mock connection and cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor
        
        # Mock the connection manager
        self.connection_patch = patch('forestfire.database.repository.DatabaseConnectionManager.get_connection')
        self.mock_get_connection = self.connection_patch.start()
        self.mock_get_connection.return_value.__enter__.return_value = self.mock_conn
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.connection_patch.stop()
    
    def test_execute_query_select(self):
        """Test executing a SELECT query"""
        # Mock data to be returned by the cursor
        mock_data = [
            (1, 'item1'),
            (2, 'item2')
        ]
        self.mock_cursor.fetchall.return_value = mock_data
        self.mock_cursor.description = True  # Indicate that this is a SELECT query
        
        # Execute a query
        query = "SELECT * FROM items WHERE id = %s"
        params = (1,)
        result = self.repository.execute_query(query, params)
        
        # Check that the cursor methods were called correctly
        self.mock_cursor.execute.assert_called_once_with(query, params)
        self.mock_cursor.fetchall.assert_called_once()
        
        # Check that the result matches the mock data
        self.assertEqual(result, mock_data)
    
    def test_execute_query_insert(self):
        """Test executing an INSERT query"""
        # Mock cursor for INSERT query (no results)
        self.mock_cursor.description = None  # Indicate that this is not a SELECT query
        
        # Execute a query
        query = "INSERT INTO items (name) VALUES (%s)"
        params = ('new_item',)
        result = self.repository.execute_query(query, params)
        
        # Check that the cursor methods were called correctly
        self.mock_cursor.execute.assert_called_once_with(query, params)
        self.mock_cursor.fetchall.assert_not_called()
        
        # Check that an empty list is returned
        self.assertEqual(result, [])
    
    def test_execute_query_error(self):
        """Test error handling when executing a query"""
        # Mock cursor to raise an exception
        self.mock_cursor.execute.side_effect = psycopg2.Error("Database error")
        
        # Execute a query and check that it raises QueryError
        query = "SELECT * FROM items"
        with self.assertRaises(QueryError):
            self.repository.execute_query(query)
        
        # Check that the cursor method was called
        self.mock_cursor.execute.assert_called_once()
    
    def test_execute_transaction_success(self):
        """Test executing a successful transaction"""
        # Prepare queries for transaction
        queries = [
            ("INSERT INTO items (name) VALUES (%s)", ('item1',)),
            ("INSERT INTO items (name) VALUES (%s)", ('item2',))
        ]
        
        # Execute transaction
        self.repository.execute_transaction(queries)
        
        # Check that cursor.execute was called for each query
        self.assertEqual(self.mock_cursor.execute.call_count, 2)
        
        # Check that commit was called
        self.mock_conn.commit.assert_called_once()
        self.mock_conn.rollback.assert_not_called()
    
    def test_execute_transaction_error(self):
        """Test error handling when executing a transaction"""
        # Prepare queries for transaction
        queries = [
            ("INSERT INTO items (name) VALUES (%s)", ('item1',)),
            ("INSERT INTO items (name) VALUES (%s)", ('item2',))
        ]
        
        # Mock cursor to raise an exception on the second query
        self.mock_cursor.execute.side_effect = [None, psycopg2.Error("Database error")]
        
        # Execute transaction and check that it raises QueryError
        with self.assertRaises(QueryError):
            self.repository.execute_transaction(queries)
        
        # Check that rollback was called
        self.mock_conn.commit.assert_not_called()
        self.mock_conn.rollback.assert_called_once()
    
    def test_execute_transaction_empty(self):
        """Test executing an empty transaction"""
        # Empty list of queries
        queries = []
        
        # Execute transaction
        self.repository.execute_transaction(queries)
        
        # Check that cursor.execute was not called
        self.mock_cursor.execute.assert_not_called()
        
        # Check that commit was still called
        self.mock_conn.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
