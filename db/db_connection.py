import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "cloud_inventory",
    "user": "inventory_user",
    "password": "strongpassword123"
}

def get_connection():
    """Create and return a PostgreSQL DB connection."""
    try:
        conn = psycopg2.connect(
            **DB_CONFIG,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print("❌ Error connecting to PostgreSQL:", e)
        raise


