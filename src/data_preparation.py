"""
Database access functions for Supabase using Streamlit secrets. Loads data and ensures correct dtypes, and creates additional columns.
"""
import os
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from utilities.transforms import create_period_columns, create_universal_amount


@st.cache_resource
def get_supabase() -> Client:
    """
    Initialize and return Supabase client.
    Cached with st.cache_resource to reuse the client across sessions.
    
    On Heroku (production), reads credentials from environment variables.
    On local development, reads from Streamlit secrets.
    """
    # Check if running on Heroku (production)
    is_production = os.environ.get("DYNO") is not None
    
    if is_production:
        # Heroku: read from environment variables
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
    else:
        # Local: read from Streamlit secrets
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    
    if not url or not key:
        raise ValueError(
            "Supabase credentials not found. "
            "Set SUPABASE_URL and SUPABASE_KEY in environment variables (production) "
            "or in .streamlit/secrets.toml (local development)."
        )
    
    return create_client(url, key)


@st.cache_data(ttl=600)
def load_transactions() -> pd.DataFrame:
    """
    Load transactions from Supabase and return as pandas DataFrame.
    
    Returns:
        pd.DataFrame: Transactions with correct dtypes:
            - date: timezone-aware datetime (UTC)
            - amount: float
    """
    supabase = get_supabase()
    
    # Query transactions table with pagination (Supabase limits to 1000 rows by default)
    all_rows = []
    start = 0
    batch_size = 1000
    while True:
        response = supabase.table("transactions").select("*").range(start, start + batch_size - 1).execute()
        rows = response.data
        all_rows.extend(rows)
        if len(rows) < batch_size:
            break
        start += batch_size
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(all_rows)

    # add log of the load with date range and number of records
    print(f"Loaded {len(df)} transactions from Supabase.")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Ensure correct dtypes
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], utc=True)
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").astype(float)
    
    # Create new columns
    df = create_period_columns(df)
    df = create_universal_amount(df)

    # reorder columns
    cols = df.columns.tolist()
    if "amount" in cols and "amount_universal_clp" in cols:
        cols.remove("amount_universal_clp")
        amount_index = cols.index("currency")
        cols.insert(amount_index + 1, "amount_universal_clp")
        df = df[cols]

    return df


