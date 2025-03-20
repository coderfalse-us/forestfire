from contextlib import contextmanager
from typing import Generator
import psycopg2
from .config import DatabaseConfig
from .exceptions import ConnectionError

class DatabaseConnectionManager:
    _config = DatabaseConfig()
    _connection = None

    @classmethod
    @contextmanager
    def get_connection(cls) -> Generator[psycopg2.extensions.connection, None, None]:
        try:
            if not cls._connection or cls._connection.closed:
                cls._connection = psycopg2.connect(
                    host=cls._config.host,
                    port=cls._config.port,
                    database=cls._config.database,
                    user=cls._config.user,
                    password=cls._config.password
                )
            yield cls._connection
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")
        finally:
            if cls._connection and not cls._connection.closed:
                cls._connection.close()