"""Tests for the DatabaseConnectionManager class.

This module contains tests for the DatabaseConnectionManager class used for
managing database connections in the warehouse order picking system.
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import psycopg2
from forestfire.database.connection import DatabaseConnectionManager
from forestfire.database.exceptions import DBConnectionError


class TestDatabaseConnectionManager:
    """Test cases for the DatabaseConnectionManager class."""

    def setup_method(self):
        """Reset the connection before each test."""
        # Reset the class variable to ensure tests are isolated
        DatabaseConnectionManager._connection = None

    def teardown_method(self):
        """Clean up after each test."""
        # Reset the class variable after each test
        DatabaseConnectionManager._connection = None

    @patch("psycopg2.connect")
    def test_get_connection_creates_new_connection(self, mock_connect):
        """Test that get_connection creates a new connection when none exists."""
        # Arrange
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Act
        with DatabaseConnectionManager.get_connection() as conn:
            # Assert
            assert conn is mock_conn
            mock_connect.assert_called_once()

    @patch("psycopg2.connect")
    def test_get_connection_reuses_existing_connection(self, mock_connect):
        """Test that get_connection reuses an existing connection."""
        # Arrange
        mock_conn = MagicMock()
        mock_conn.closed = False
        mock_connect.return_value = mock_conn

        # Create an initial connection
        with DatabaseConnectionManager.get_connection():
            pass

        # Reset the mock to check if it's called again
        mock_connect.reset_mock()

        # Act - use the connection again
        with DatabaseConnectionManager.get_connection() as conn:
            # Assert
            assert conn is mock_conn
            mock_connect.assert_not_called()  # Should not create a new connection

    @patch("psycopg2.connect")
    def test_get_connection_creates_new_when_closed(self, mock_connect):
        """Test that get_connection creates a new connection when the existing one is closed."""
        # Arrange
        mock_conn1 = MagicMock()
        mock_conn1.closed = False
        mock_conn2 = MagicMock()
        mock_conn2.closed = False

        # First call returns conn1, second call returns conn2
        mock_connect.side_effect = [mock_conn1, mock_conn2]

        # Create an initial connection
        with DatabaseConnectionManager.get_connection():
            pass

        # Simulate the connection being closed
        mock_conn1.closed = True

        # Act - get a new connection
        with DatabaseConnectionManager.get_connection() as conn:
            # Assert
            assert conn is mock_conn2
            assert mock_connect.call_count == 2  # Should create a new connection

    @patch("psycopg2.connect")
    def test_connection_is_closed_after_context(self, mock_connect):
        """Test that the connection is closed after exiting the context manager."""
        # Arrange
        mock_conn = MagicMock()
        mock_conn.closed = False
        mock_connect.return_value = mock_conn

        # Act
        with DatabaseConnectionManager.get_connection():
            pass  # Just enter and exit the context

        # Assert
        mock_conn.close.assert_called_once()

    @patch("psycopg2.connect")
    def test_connection_error_handling(self, mock_connect):
        """Test that connection errors are properly handled."""
        # Arrange
        mock_connect.side_effect = psycopg2.Error("Connection error")

        # Act/Assert
        with pytest.raises(DBConnectionError) as excinfo:
            with DatabaseConnectionManager.get_connection():
                pass  # Should raise before reaching here

        assert "Failed to connect to database" in str(excinfo.value)

    @patch("psycopg2.connect")
    def test_exception_in_context_closes_connection(self, mock_connect):
        """Test that the connection is closed even if an exception occurs in the context."""
        # Arrange
        mock_conn = MagicMock()
        mock_conn.closed = False
        mock_connect.return_value = mock_conn

        # Act
        with pytest.raises(DBConnectionError):
            with DatabaseConnectionManager.get_connection():
                raise ValueError("Test exception")

        # Assert
        mock_conn.close.assert_called_once()

    @patch("psycopg2.connect")
    def test_connection_with_config_parameters(self, mock_connect):
        """Test that connection is created with the correct config parameters."""
        # Arrange
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Create a mock config object
        mock_config = MagicMock()
        mock_config.host = "test_host"
        mock_config.port = 5432
        mock_config.database = "test_db"
        mock_config.user = "test_user"
        mock_config.password = "test_password"

        # Save the original config
        original_config = DatabaseConnectionManager._config

        try:
            # Replace the config with our mock
            DatabaseConnectionManager._config = mock_config

            # Reset any existing connection
            DatabaseConnectionManager._connection = None

            # Act
            with DatabaseConnectionManager.get_connection():
                pass

            # Assert
            mock_connect.assert_called_once_with(
                host="test_host",
                port=5432,
                database="test_db",
                user="test_user",
                password="test_password",
            )
        finally:
            # Restore the original config
            DatabaseConnectionManager._config = original_config

    @patch("psycopg2.connect")
    def test_connection_not_closed_if_already_closed(self, mock_connect):
        """Test that the connection is not closed again if it's already closed."""
        # Arrange
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # First, let's create a connection and then close it manually
        with DatabaseConnectionManager.get_connection():
            pass

        # Reset the mock to clear the call history
        mock_conn.close.reset_mock()

        # Now simulate that the connection is already closed
        mock_conn.closed = True

        # Act - use the connection manager again
        with DatabaseConnectionManager.get_connection():
            pass

        # Assert - since we're creating a new connection, the old one shouldn't be closed again
        mock_conn.close.assert_not_called()
