import os
import pandas as pd
from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy import text
import tomli

def get_db_connection():
    """
    Establishes a connection to the Cloud SQL instance using configuration from secrets.toml.
    Returns a SQLAlchemy engine.
    """
    # Load secrets
    secrets_path = ".streamlit/secrets.toml"
    # Handle cases where script is run from different directories
    if not os.path.exists(secrets_path):
        # Try finding it relative to the script location if run directly
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        secrets_path = os.path.join(project_root, ".streamlit", "secrets.toml")
        
    if not os.path.exists(secrets_path):
        raise FileNotFoundError(f"Secrets file not found at {secrets_path}")

    with open(secrets_path, "rb") as f:
        secrets = tomli.load(f)

    db_config = secrets["gcp_cloud_sql"]
    
    instance_connection_name = db_config["INSTANCE_CONNECTION_NAME"]
    db_user = db_config["DB_USER"]
    db_pass = db_config["DB_PASS"]
    db_name = db_config["DB_NAME"]

    # Define the connector creation function
    def getconn():
        with Connector() as connector:
            conn = connector.connect(
                instance_connection_name,
                "pg8000",
                user=db_user,
                password=db_pass,
                db=db_name,
            )
            return conn

    # Create the SQLAlchemy engine
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return pool

def get_existing_hashes(engine=None):
    """
    Fetches all existing record_hash values from the transactions table.
    """
    if engine is None:
        engine = get_db_connection()
        
    try:
        # Check if table exists first (or handle error)
        # Using a simple query. If table doesn't exist, this will fail, which is fine.
        query = "SELECT record_hash FROM transactions WHERE record_hash IS NOT NULL"
        df = pd.read_sql(query, engine)
        return set(df["record_hash"].tolist())
    except Exception as e:
        print(f"Error fetching existing hashes: {e}")
        # If table doesn't exist or other error, return empty set so we don't break
        # (Though if table doesn't exist, insert will fail later)
        return set()

def insert_new_transactions(df, engine=None):
    """
    Inserts new transactions into the database.
    Args:
        df: DataFrame containing the new transactions.
        engine: SQLAlchemy engine (optional).
    """
    if df.empty:
        print("No transactions to insert.")
        return 0

    if engine is None:
        engine = get_db_connection()
    
    table_name = "transactions"
    
    try:
        # Check if table exists, create if not (using the logic from load_transactions if needed)
        # For now, we assume table exists as this is an "add new" script. 
        # But we should probably use the check_and_create logic if we want to be robust.
        # Let's trust the load script did its job or the table exists.
        
        print(f"Inserting {len(df)} rows into '{table_name}'...")
        df.to_sql(table_name, engine, if_exists='append', index=False, chunksize=1000)
        print("Data inserted successfully.")
        return len(df)
    except Exception as e:
        print(f"Error inserting data: {e}")
        raise e

if __name__ == "__main__":
    # Example usage / testing
    try:
        engine = get_db_connection()
        hashes = get_existing_hashes(engine)
        print(f"Found {len(hashes)} existing transaction hashes.")
    except Exception as e:
        print(f"An error occurred: {e}")
