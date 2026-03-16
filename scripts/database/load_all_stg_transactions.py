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
CSV_DIR = "seeds/spendee_csv_exports/transactions_export_2026-03-16"

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
    # Schema definition based on CSV: Date,Wallet,Type,"Category name",Amount,Currency,Note,Labels,Author
    
    # Drop table first to recreate with new schema if needed
    drop_stmt = text(f"DROP TABLE IF EXISTS {TABLE_NAME};")
    
    create_stmt = text(f"""
        CREATE TABLE {TABLE_NAME} (
            "Date" TIMESTAMPTZ,
            "Wallet" TEXT,
            "Type" TEXT,
            "Category name" TEXT,
            "Amount" NUMERIC,
            "Currency" TEXT,
            "Note" TEXT,
            "Labels" TEXT,
            "Author" TEXT
        );
    """)
    with engine.connect() as conn:
        conn.execute(drop_stmt)
        conn.execute(create_stmt)
        conn.commit()
    print(f"Table '{TABLE_NAME}' check complete. Recreated with new schema if it existed.")

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

def reload_all_transactions_to_database(engine, csv_dir):
    """
    Orchestrates the reloading of all transaction data:
    1. Ensures the table exists.
    2. Clears the table.
    3. Loads fresh data from all CSVs in the directory.
    """
    if not os.path.exists(csv_dir):
        print(f"Error: Directory '{csv_dir}' not found.")
        return

    # 1. Ensure table structure is present
    check_and_create_table(engine)
    
    # 2. Clear existing data
    clear_table(engine)
    
    # 3. Process all CSV files in directory
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    if not csv_files:
        print(f"No CSV files found in '{csv_dir}'.")
        return
        
    for file in csv_files:
        csv_path = os.path.join(csv_dir, file)
        print(f"Reading data from '{csv_path}'...")
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            print(f"Error reading CSV file {file}: {e}")
            continue
            
        if df.empty:
            print(f"CSV file {file} is empty. Skipping.")
            continue
        
        # Ensure Date column is parsed as datetime (Postgres expects appropriate format)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        
        print(f"Prepared {len(df)} rows from {file} for insertion.")
        
        # 4. Insert Data
        print(f"Inserting data from {file} into '{TABLE_NAME}'...")
        try:
            # Use 'append' because the table exists (we just cleared it)
            df.to_sql(TABLE_NAME, engine, if_exists='append', index=False, chunksize=1000)
            print(f"Data from {file} loaded successfully.")
        except Exception as e:
            print(f"Error inserting data from {file}: {e}")
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
        reload_all_transactions_to_database(pool, CSV_DIR)
    except Exception as e:
        print(f"An error occurred during execution: {e}")
    finally:
        pool.dispose()

if __name__ == "__main__":
    main()
