"""Tests for the BaseRepository class.

This module contains tests for the BaseRepository class used for
database operations in the warehouse order picking system.
"""

import pytest
from unittest.mock import patch, MagicMock
import psycopg2
from forestfire.database.repository import BaseRepository
from forestfire.database.exceptions import QueryError


class TestBaseRepositoryComprehensive:
    """Comprehensive test cases for the BaseRepository class."""

    @patch('forestfire.database.connection.DatabaseConnectionManager'
           '.get_connection')
    def test_execute_query_select(self, mock_get_connection):
        """Test executing a SELECT query."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = True  # Indicates a SELECT query
        mock_cursor.fetchall.return_value = [('row1',), ('row2',)]
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        repo = BaseRepository()
        query = 'SELECT * FROM test_table'
        params = ('param1',)

        # Act
        result = repo.execute_query(query, params)

        # Assert
        mock_cursor.execute.assert_called_once_with(query, params)
        mock_cursor.fetchall.assert_called_once()
        assert result == [('row1',), ('row2',)]

    @patch('forestfire.database.connection.DatabaseConnectionManager'
           '.get_connection')
    def test_execute_query_insert(self, mock_get_connection):
        """Test executing an INSERT query."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = None  # Indicates a non-SELECT query
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        repo = BaseRepository()
        query = 'INSERT INTO test_table VALUES (%s)'
        params = ('value1',)

        # Act
        result = repo.execute_query(query, params)

        # Assert
        mock_cursor.execute.assert_called_once_with(query, params)
        mock_cursor.fetchall.assert_not_called()
        assert result == []

    @patch('forestfire.database.connection.DatabaseConnectionManager'
           '.get_connection')
    def test_execute_query_error(self, mock_get_connection):
        """Test handling errors when executing a query."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = psycopg2.Error('Database error')
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        repo = BaseRepository()
        query = 'SELECT * FROM test_table'

        # Act/Assert
        with pytest.raises(QueryError) as excinfo:
            repo.execute_query(query)
        assert 'Query execution failed' in str(excinfo.value)
        mock_cursor.execute.assert_called_once()

    @patch('forestfire.database.connection.DatabaseConnectionManager'
           '.get_connection')
    def test_execute_transaction_success(self, mock_get_connection):
        """Test executing a successful transaction."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        repo = BaseRepository()
        queries = [
            ('INSERT INTO test_table VALUES (%s)', ('value1',)),
            ('UPDATE test_table SET col = %s', ('value2',))
        ]

        # Act
        repo.execute_transaction(queries)

        # Assert
        assert mock_cursor.execute.call_count == 2
        mock_cursor.execute.assert_any_call(queries[0][0], queries[0][1])
        mock_cursor.execute.assert_any_call(queries[1][0], queries[1][1])
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

    @patch('forestfire.database.connection.DatabaseConnectionManager'
           '.get_connection')
    def test_execute_transaction_error(self, mock_get_connection):
        """Test handling errors in a transaction."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception('Transaction error')
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        repo = BaseRepository()
        queries = [
            ('INSERT INTO test_table VALUES (%s)', ('value1',)),
            ('UPDATE test_table SET col = %s', ('value2',))
        ]

        # Act/Assert
        with pytest.raises(QueryError) as excinfo:
            repo.execute_transaction(queries)
        assert 'Transaction failed' in str(excinfo.value)
        mock_cursor.execute.assert_called_once_with(queries[0][0],
                                                    queries[0][1])
        mock_conn.commit.assert_not_called()
        mock_conn.rollback.assert_called_once()

    @patch('forestfire.database.connection.DatabaseConnectionManager'
           '.get_connection')
    def test_execute_transaction_empty(self, mock_get_connection):
        """Test executing an empty transaction."""
        # Arrange
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        repo = BaseRepository()
        queries = []

        # Act
        repo.execute_transaction(queries)

        # Assert
        mock_cursor.execute.assert_not_called()
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

