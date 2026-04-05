#!/usr/bin/env python3
import os
import sys
import pandas as pd
import sqlalchemy
from sqlalchemy import text
import tomli

from helpers.constants.wallets import WALLETS
from helpers.data_transformations.spendee_clean import add_spendee_record_hash
from helpers.gcs_handler import download_db, upload_db

LOCAL_DB_PATH = "/tmp/expenses.sqlite"
STAGING_TABLE = "stg_transaction"


def get_db_connection():
    """
    Returns a SQLAlchemy engine pointing at the local SQLite file.
    Call download_db() before this if running outside of Streamlit.
    """
    engine = sqlalchemy.create_engine(
        f"sqlite:///{LOCAL_DB_PATH}",
        connect_args={"check_same_thread": False},
    )
    return engine

def get_latest_transaction_date(engine=None):
    """
    Fetches the most recent date from the transactions table.
    """
    if engine is None:
        engine = get_db_connection()
        
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT MAX(date) as max_date FROM stg_transaction"))
            row = result.fetchone()
            max_date = row[0] if row else None
            if max_date is not None and pd.notnull(max_date):
                return pd.to_datetime(max_date)
            return None
    except Exception as e:
        print(f"Error fetching latest date: {e}")
        return None

def insert_new_transactions(df, engine=None):
    """
    Inserts new transactions into the staging table.
    Args:
        df: DataFrame containing the new transactions.
        engine: SQLAlchemy engine (optional).
    """
    if df.empty:
        print("No transactions to insert.")
        return 0

    if engine is None:
        engine = get_db_connection()
    
    try:
        print(f"Inserting {len(df)} rows into '{STAGING_TABLE}'...")
        with engine.begin() as conn:
            df.to_sql(STAGING_TABLE, conn, if_exists='append', index=False, chunksize=1000)
        print("Data inserted successfully.")
        upload_db()   # sync to GCS immediately
        return len(df)
    except Exception as e:
        print(f"Error inserting data: {e}")
        raise e

if __name__ == "__main__":
    import re

    try:
        # Handle cases where script is run from different directories
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Add project root to sys.path to allow importing from helpers
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        # Download the SQLite DB from GCS before querying
        print("Downloading SQLite DB from GCS...")
        download_db(force=True)
        
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
        
        import datetime
        
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
                    # Get the actual file modification date in YYYY-MM-DD format
                    file_path = os.path.join(search_dir, f)
                    mtime = os.path.getmtime(file_path)
                    date_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
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
