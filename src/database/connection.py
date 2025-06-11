"""Database connection management module.

This module provides functionality for managing database connections
and ensuring proper connection handling with context managers.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncpg
from .config import DatabaseConfig
from .exceptions import DBConnectionError


class DatabaseConnectionManager:
    """Manages database connections using a singleton pattern.

    This class provides methods to get database connections and ensures
    proper connection handling and resource cleanup.
    """

    _config = DatabaseConfig()
    _pool = None

    @classmethod
    def get_config(cls):
        """Get the current database configuration.

        Returns:
            DatabaseConfig: The current database configuration
        """
        return cls._config

    @classmethod
    def set_config(cls, config):
        """Set a new database configuration.

        Args:
            config: The new database configuration to use
        """
        cls._config = config

    @classmethod
    async def create_pool(
        cls,
    ):
        """Create a connection pool if it does not exist."""
        if not cls._pool:
            cls._pool = await asyncpg.create_pool(
                host=cls._config.host,
                port=cls._config.port,
                database=cls._config.database,
                user=cls._config.user,
                password=cls._config.password,
                min_size=5,
                max_size=20,
            )

    @classmethod
    @asynccontextmanager
    async def get_connection(cls) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a database connection from the pool"""
        if not cls._pool:
            await cls.create_pool()

        try:
            async with cls._pool.acquire() as connection:
                yield connection
        except Exception as e:
            raise DBConnectionError(
                f"Failed to connect to database: {e}"
            ) from e

    @classmethod
    async def close_pool(cls):
        """Close the connection pool"""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
