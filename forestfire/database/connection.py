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
    def get_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
        try:
            if not self._connection or self._connection.closed:
                self._connection = psycopg2.connect(
                    host=self._config.host,
                    port=self._config.port,
                    database=self._config.database,
                    user=self._config.user,
                    password=self._config.password
                )
            yield self._connection
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")
        finally:
            if self._connection and not self._connection.closed:
                self._connection.close()