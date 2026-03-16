"""This script reloads all transaction data from a CSV file into a Google Cloud SQL PostgreSQL database, clearing existing records first."""

import os
import pandas as pd
from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy import text
import tomli

# Configuration
with open(".streamlit/secrets.toml", "rb") as f:
    secrets = tomli.load(f)

db_config = secrets["gcp_cloud_sql"]

INSTANCE_CONNECTION_NAME = db_config["INSTANCE_CONNECTION_NAME"]
DB_USER = db_config["DB_USER"]
DB_PASS = db_config["DB_PASS"]
DB_NAME = db_config["DB_NAME"]
TABLE_NAME = "stg_transaction"
CSV_FILE = db_config["CSV_FILE"]

def getconn():
    """Establishes a connection to the Cloud SQL instance."""
    with Connector() as connector:
        conn = connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pg8000",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
        )
        return conn

def check_and_create_table(engine):
    """
    Checks if the transactions table exists and creates it if not.
    Schema is based on the known CSV structure.
    """
    print(f"Checking if table '{TABLE_NAME}' exists...")
    # Schema definition
    create_stmt = text(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            date TIMESTAMPTZ,
            wallet TEXT,
            type TEXT,
            category TEXT,
            amount NUMERIC,
            currency TEXT,
            note TEXT,
            labels TEXT,
            author TEXT,
            record_hash TEXT
        );
    """)
    with engine.connect() as conn:
        conn.execute(create_stmt)
        conn.commit()
    print(f"Table '{TABLE_NAME}' check complete.")

def clear_table(engine):
    """
    Deletes all rows from the transactions table using TRUNCATE.
    """
    print(f"Clearing all data from '{TABLE_NAME}'...")
    with engine.connect() as conn:
        # TRUNCATE is faster than DELETE for removing all rows
        conn.execute(text(f"TRUNCATE TABLE {TABLE_NAME};"))
        conn.commit()
    print(f"All rows deleted from '{TABLE_NAME}'.")

def reload_all_transactions_to_database(engine, csv_path):
    """
    Orchestrates the reloading of all transaction data:
    1. Ensures the table exists.
    2. Clears the table.
    3. Loads fresh data from the CSV.
    """
    if not os.path.exists(csv_path):
        print(f"Error: File '{csv_path}' not found.")
        return

    # 1. Ensure table structure is present
    check_and_create_table(engine)
    
    # 2. Clear existing data
    clear_table(engine)
    
    # 3. Read and Prepare Data
    print(f"Reading data from '{csv_path}'...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
        
    if df.empty:
        print("CSV file is empty. Nothing to load.")
        return
    
    # Ensure date column is parsed as datetime (Postgres expects appropriate format)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    print(f"Prepared {len(df)} rows for insertion.")
    
    # 4. Insert Data
    print(f"Inserting data into '{TABLE_NAME}'...")
    try:
        # Use 'append' because the table exists (we just cleared it)
        df.to_sql(TABLE_NAME, engine, if_exists='append', index=False, chunksize=1000)
        print("Data reloaded successfully.")
    except Exception as e:
        print(f"Error inserting data: {e}")
        # Re-raise or handle as appropriate
        raise e

def main():
    """Main execution entry point."""
    # Create the SQLAlchemy engine with the Cloud SQL connector
    # The 'creator' argument specifies the callable that returns the connection
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )

    try:
        reload_all_transactions_to_database(pool, CSV_FILE)
    except Exception as e:
        print(f"An error occurred during execution: {e}")
    finally:
        pool.dispose()

if __name__ == "__main__":
    main()
