from dataclasses import dataclass
import os
from dotenv import load_dotenv
from pathlib import Path

# env_path = Path(__file__).parent.parent.parent / '.env'
# load_dotenv(env_path)
load_dotenv()

@dataclass
class DatabaseConfig:
    host: str = os.getenv('DB_HOST')
    port: int = int(os.getenv('DB_PORT'))
    database: str = os.getenv('DB_NAME')
    user: str = os.getenv('DB_USER')
    password: str = os.getenv('DB_PASSWORD')
    pool_size: int = int(os.getenv('DB_POOL_SIZE', 5))
    pool_timeout: int = int(os.getenv('DB_POOL_TIMEOUT', 30))