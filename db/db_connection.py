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

def get_vmname(vmname):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT vm_name FROM vm_inventory WHERE vm_name = %s"
        cursor.execute(query, (vmname,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print("❌ Error fetching VM by name:", e)
        raise


