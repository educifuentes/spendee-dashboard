"""
Test loading transactions from Supabase database.
"""
import sys
from pathlib import Path

import pandas as pd
import tomli as tomllib
from supabase import create_client, Client


def load_transactions_test():
    """Load transactions from Supabase (test version without Streamlit)."""
    # Load secrets from .streamlit/secrets.toml
    secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"
    with open(secrets_path, "rb") as f:
        secrets = tomllib.load(f)
    
    # Initialize Supabase client
    url = secrets["SUPABASE_URL"]
    key = secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    
    # Query transactions table, ordered by date
    response = supabase.table("transactions").select("*").order("date").execute()
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(response.data)
    
    # Ensure correct dtypes
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], utc=True)
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").astype(float)
    
    return df


if __name__ == "__main__":
    try:
        df = load_transactions_test()
        print(f"DataFrame shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"\nFirst few rows:")
        print(df.head())
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

