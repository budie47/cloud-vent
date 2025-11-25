from db_connection import get_connection

def init_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vm_inventory (
            id SERIAL PRIMARY KEY,
            subscription_id TEXT,
            resource_group TEXT,
            vm_name TEXT,
            location TEXT,
            power_state TEXT,
            os_type TEXT,
            version TEXT,
            private_ip TEXT,
            public_ip TEXT,
            vm_size TEXT,
            tags JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("✔ PostgreSQL tables initialized successfully.")

if __name__ == "__main__":
    init_tables()
