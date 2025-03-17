import psycopg2

def connect_to_db():
    DB_HOST = "alspgbdvit01q.ohl.com"
    DB_NAME = "vite_picking_d_qa"
    DB_USER = "usr_synpick"
    DB_PASSWORD = "Niermftyg934"
    DB_PORT = "6432"

    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        print("Database connection successful!")
        return connection
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {e}")


def close_connection(connection):
    """Safely close database connection"""
    if connection:
        connection.close()