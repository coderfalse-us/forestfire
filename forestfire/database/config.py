"""Database configuration module.

This module provides configuration settings for database connections
loaded from environment variables.
"""

from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    """Database configuration settings.

    Attributes:
        host: Database server hostname
        port: Database server port
        database: Database name
        user: Database username
        password: Database password
        pool_size: Connection pool size
        pool_timeout: Connection pool timeout in seconds
    """
    host: str = os.getenv('DB_HOST')
    port: int = int(os.getenv('DB_PORT'))
    database: str = os.getenv('DB_NAME')
    user: str = os.getenv('DB_USER')
    password: str = os.getenv('DB_PASSWORD')
    pool_size: int = int(os.getenv('DB_POOL_SIZE', '5'))
    pool_timeout: int = int(os.getenv('DB_POOL_TIMEOUT', '30'))
