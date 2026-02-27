#!/usr/bin/env python3
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

    connector = Connector()
    # Define the connector creation function
    def getconn():
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

def get_latest_transaction_date(engine=None):
    """
    Fetches the most recent date from the transactions table.
    """
    if engine is None:
        engine = get_db_connection()
        
    try:
        query = "SELECT MAX(date) as max_date FROM transactions"
        df = pd.read_sql(query, engine)
        max_date = df["max_date"].iloc[0]
        if pd.notnull(max_date):
            return pd.to_datetime(max_date)
        return None
    except Exception as e:
        print(f"Error fetching latest date: {e}")
        return None

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
    import re
    import sys

    try:
        # Handle cases where script is run from different directories
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Add project root to sys.path to allow importing from utilities
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        from utilities.constants.wallets import WALLETS
        from utilities.data_transformations.spendee_clean import add_spendee_record_hash
        
        # Define the path to the seeds directory
        # The user's exports are either here or in seeds/new_transaction uploads
        seeds_dir = os.path.join(project_root, "seeds")
        uploads_dir = os.path.join(seeds_dir, "new_transaction uploads")
        
        directories_to_scan = [seeds_dir, uploads_dir]
        
        print(f"Scanning directories for wallet data: {directories_to_scan}")
        print(f"Configured wallets to process: {WALLETS}")
        
        # We need to find the CSV export for each wallet in the configured WALLETS list
        latest_files = {}
        
        # Pattern 1: With date (transactions_export_YYYY-MM-DD_walletname.csv)
        pattern_with_date = re.compile(r"transactions_export_(\d{4}-\d{2}-\d{2})_(.+)\.csv")
        # Pattern 2: Without date (transactions_export_walletname.csv)
        pattern_no_date = re.compile(r"transactions_export_(.+)\.csv")
        
        for search_dir in directories_to_scan:
            if not os.path.exists(search_dir):
                continue
                
            for f in os.listdir(search_dir):
                match_date = pattern_with_date.match(f)
                match_no_date = pattern_no_date.match(f)
                
                date_str = None
                wallet_name = None
                
                if match_date:
                    date_str = match_date.group(1)
                    wallet_name = match_date.group(2)
                elif match_no_date:
                    # Fake a high date so the un-dated latest export is always chosen
                    # over any dated backups if they happen to both exist.
                    date_str = "9999-99-99"
                    wallet_name = match_no_date.group(1)
                    
                # Check if this profile is one of the target wallets
                if wallet_name and wallet_name in WALLETS:
                    # Keep track of the file with the most recent date for each wallet
                    if wallet_name not in latest_files or date_str > latest_files[wallet_name]['date']:
                        latest_files[wallet_name] = {'date': date_str, 'file': os.path.join(search_dir, f)}
        
        if not latest_files:
            print("No matching CSV files found for the configured wallets.")
            exit(0)
            
        print(f"\nFound latest files for {len(latest_files)} wallets:")
        df_list = []
        
        # Raw Spendee Export Column Mapping
        rename_map = {
            "Date": "date",
            "Wallet": "wallet",
            "Type": "type",
            "Category name": "category",
            "Amount": "amount",
            "Currency": "currency",
            "Note": "note",
            "Labels": "labels",
            "Author": "author"
        }
        
        for wallet, info in latest_files.items():
            file_path = info['file']
            file_date = info['date']
            print(f" - {wallet}: {os.path.basename(file_path)} (Date: {file_date})")
            
            # Read the CSV and append to list
            try:
                wallet_df = pd.read_csv(file_path)
                
                # Standardize columns to database schema
                wallet_df = wallet_df.rename(columns=rename_map)
                
                # Only keep columns we care about if extra ones exist
                keep_cols = [c for c in rename_map.values() if c in wallet_df.columns]
                wallet_df = wallet_df[keep_cols]
                
                df_list.append(wallet_df)
            except Exception as e:
                print(f"   Error reading {file_path}: {e}")
                
        if not df_list:
            print("Failed to read any data from the files.")
            exit(1)
            
        # Combine all wallet dataframes into one
        df = pd.concat(df_list, ignore_index=True)
        print(f"\nCombined DataFrame has {len(df)} total rows.")
        
        # Generate the required record_hash for the database
        df = add_spendee_record_hash(df)
        
        engine = get_db_connection()
        
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors='coerce')
            
        latest_date = get_latest_transaction_date(engine)
        
        if latest_date is not None:
            print(f"Latest transaction in database is from: {latest_date}")
            # Align timezones if necessary for comparison
            csv_tz = getattr(df["date"].dt, 'tz', None)
            
            if latest_date.tzinfo is not None and csv_tz is None:
                df["date"] = df["date"].dt.tz_localize(latest_date.tzinfo)
            elif latest_date.tzinfo is None and csv_tz is not None:
                df["date"] = df["date"].dt.tz_localize(None)
                
            new_df = df[df["date"] > latest_date]
        else:
            print("No existing transactions found or could not fetch latest date. Inserting all rows.")
            new_df = df
        
        if new_df.empty:
            print("No new transactions to insert.")
        else:
            print(f"Found {len(new_df)} new transactions to insert.")
            insert_new_transactions(new_df, engine)
            
    except Exception as e:
        print(f"An error occurred: {e}")
