"""Tests for the BaseRepository class.

This module contains tests for the BaseRepository class used for
database operations in the warehouse order picking system.
"""

import pytest
from unittest.mock import patch, AsyncMock
import asyncpg
from forestfire.database.repository import BaseRepository
from forestfire.database.exceptions import QueryError


class DummyAsyncContextManager:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class TestBaseRepositoryComprehensive:
    """Comprehensive test cases for the BaseRepository class."""

    @pytest.mark.asyncio
    @patch(
        "forestfire.database.connection."
        "DatabaseConnectionManager.get_connection"
    )
    async def test_execute_query_select(self, mock_get_connection):
        """Test executing a SELECT query."""
        # Arrange
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [("row1",), ("row2",)]
        mock_conn.__enter__.return_value = mock_conn
        mock_get_connection.return_value.__aenter__.return_value = mock_conn

        repo = BaseRepository()
        query = "SELECT * FROM test_table"
        params = ("param1",)

        # Act
        result = await repo.execute_query(query, params)

        # Assert
        assert mock_conn.fetch.call_count == 1
        assert result == [("row1",), ("row2",)]

    @pytest.mark.asyncio
    @patch(
        "forestfire.database.connection."
        "DatabaseConnectionManager.get_connection"
    )
    async def test_execute_query_error(self, mock_get_connection):
        """Test handling errors when executing a query."""
        # Arrange
        mock_conn = AsyncMock()
        mock_conn.fetch.side_effect = asyncpg.exceptions.PostgresError(
            "Database error"
        )
        mock_get_connection.return_value.__aenter__.return_value = mock_conn

        repo = BaseRepository()
        query = "SELECT * FROM test_table"

        # Act/Assert
        with pytest.raises(QueryError) as excinfo:
            await repo.execute_query(query)
        assert "Query execution failed" in str(excinfo.value)
        mock_conn.fetch.assert_called_once()

    class DummyAsyncContextManager:
        async def __aenter__(self):
            return None

        async def __aexit__(self, *a):
            pass

    @pytest.mark.asyncio
    @patch(
        "forestfire.database.connection."
        "DatabaseConnectionManager.get_connection"
    )
    async def test_execute_transaction_empty(self, mock_get_connection):
        """Test executing an empty transaction."""
        # Arrange
        mock_conn = AsyncMock()
        mock_conn.__aenter__.return_value = mock_conn

        def dummy_transaction():
            return DummyAsyncContextManager()

        mock_conn.transaction = dummy_transaction
        mock_get_connection.return_value.__aenter__.return_value = mock_conn

        repo = BaseRepository()
        queries = []

        # Act
        await repo.execute_transaction(queries)

        # Assert
        mock_conn.execute.assert_not_called()
        mock_conn.commit.assert_not_called()
        mock_conn.rollback.assert_not_called()
