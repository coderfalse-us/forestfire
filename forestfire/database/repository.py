"""Base repository module for database operations.

This module provides a base repository class with common database operations
like executing queries and transactions with proper error handling.
"""

from abc import ABC
from typing import Any, List
import psycopg2
from .connection import DatabaseConnectionManager
from .exceptions import QueryError

class BaseRepository(ABC):
    """Base repository class for database operations.

    Provides common methods for executing queries and transactions
    with proper connection handling and error reporting.
    """
    def execute_query(self, query: str, params: tuple = None) -> List[Any]:
        with DatabaseConnectionManager.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(query, params)
                    return cur.fetchall() if cur.description else []
                except psycopg2.Error as e:
                    raise QueryError(f"Query execution failed: {e}") from e

    def execute_transaction(self, queries: List[tuple]) -> None:
        with DatabaseConnectionManager.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    for query, params in queries:
                        cur.execute(query, params)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    raise QueryError(f"Transaction failed: {e}") from e
