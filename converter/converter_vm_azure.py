import sys
import os

# Dynamically add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import psycopg2
from db.db_connection import get_connection, get_vmname  

# File picker
import tkinter as tk
from tkinter import filedialog


def insert_vm_row(cursor, row):
    """Insert a single VM row into PostgreSQL."""

    query = """
        INSERT INTO vm_inventory 
        (subscription_id, resource_group, vm_name, location,
         power_state, os_type, version, private_ip, public_ip, vm_size, tags)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        row["subscription_id"],
        row["resource_group"],
        row["vm_name"],
        row["location"],
        row["power_state"],
        row["os_type"],
        row["version"],
        row["private_ip"],
        row["public_ip"],
        row["vm_size"],
        row.get("tags")  # stored as JSONB
    ))

def check_vm_exists(vm_name):
    """Check if a VM with the given name exists in the database."""
    result = get_vmname(vm_name)
    return result is not None

def pick_csv_file():
    """Open a Windows/macOS/Linux file picker dialog."""
    root = tk.Tk()
    root.withdraw()  # hide main window

    file_path = filedialog.askopenfilename(
        title="Select Azure VM Inventory CSV File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    return file_path


def convert_csv_to_postgres(csv_file):
    print(f"Loading CSV file: {csv_file}")
    df = pd.read_csv(csv_file)
    df = df.where(pd.notnull(df), None)  # replace NaN with None for Postgres

    conn = get_connection()
    cursor = conn.cursor()

    print(f"Inserting {len(df)} rows into PostgreSQL...")

    for _, row in df.iterrows():
        if check_vm_exists(row["vm_name"]):
            print(f"⚠ VM '{row['vm_name']}' already exists. Skipping insertion.")
            continue
        else:
            insert_vm_row(cursor, row)

    conn.commit()
    cursor.close()
    conn.close()

    print("✔ CSV successfully imported into PostgreSQL.")


if __name__ == "__main__":

    # If CSV file was passed as a command argument
    if len(sys.argv) == 2:
        convert_csv_to_postgres(sys.argv[1])
    else:
        print("📁 No CSV file specified — opening file picker...")
        csv_path = pick_csv_file()

        if not csv_path:
            print("❌ No file selected. Exiting.")
            exit(1)

        convert_csv_to_postgres(csv_path)
