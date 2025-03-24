class DatabaseError(Exception):
    """Base exception for database errors"""
    pass

class ConnectionError(DatabaseError):
    """Raised when database connection fails"""
    pass

class QueryError(DatabaseError):
    """Raised when query execution fails"""
    pass