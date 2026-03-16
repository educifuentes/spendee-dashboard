"""Script to create the stg_transaction table with adhoc structure in Google Cloud SQL."""

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

def create_table(engine):
    """
    Creates the stg_transaction table with adhoc structure if it does not exist.
    """
    print(f"Creating table '{TABLE_NAME}' if it doesn't exist...")
    
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
    print(f"Table '{TABLE_NAME}' creation script executed successfully.")

def main():
    """Main execution entry point."""
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )

    try:
        create_table(pool)
    except Exception as e:
        print(f"An error occurred during execution: {e}")
    finally:
        pool.dispose()

if __name__ == "__main__":
    main()
