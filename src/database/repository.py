"""Base repository module for database operations.

This module provides a base repository class with common database operations
like executing queries and transactions with proper error handling.
"""

from abc import ABC
from typing import Any, List
from .connection import DatabaseConnectionManager
from .exceptions import QueryError


class BaseRepository(ABC):
    """Base repository class for database operations.

    Provides common methods for executing queries and transactions
    with proper connection handling and error reporting.
    """

    async def execute_query(
        self, query: str, params: tuple = None
    ) -> List[Any]:
        """Execute a query and return the result."""
        async with DatabaseConnectionManager.get_connection() as conn:
            try:
                # asyncpg uses different method names
                if params:
                    return await conn.fetch(query, *params)
                return await conn.fetch(query)
            except Exception as e:
                raise QueryError(f"Query execution failed: {e}") from e

    async def execute_transaction(self, queries: List[tuple]) -> None:
        """Execute a series of queries as a transaction."""
        async with DatabaseConnectionManager.get_connection() as conn:
            async with conn.transaction():
                try:
                    for query, params in queries:
                        if params:
                            await conn.execute(query, *params)
                        else:
                            await conn.execute(query)
                except Exception as e:
                    raise QueryError(f"Transaction failed: {e}") from e
