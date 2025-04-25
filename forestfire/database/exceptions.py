"""Database exception classes.

This module defines custom exception classes for database operations
to provide more specific error handling for database-related issues.
"""

class DatabaseError(Exception):
    """Base exception for database errors."""
    pass


class DBConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass


class QueryError(DatabaseError):
    """Raised when query execution fails."""
    pass
