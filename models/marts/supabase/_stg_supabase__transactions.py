
import streamlit as st
import pandas as pd

from utilities.data_conection import get_supabase
from utilities.data_transformations.periods import create_period_columns


@st.cache_data(ttl=600)
def stg_spendee__transactions() -> pd.DataFrame:
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
    
    # dtypes
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], utc=True)
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").astype(float)
    
    return df


