"""
Database access functions for Supabase using Streamlit secrets.
"""
import streamlit as st
import pandas as pd
from supabase import create_client, Client


@st.cache_resource
def get_supabase() -> Client:
    """
    Initialize and return Supabase client.
    Cached with st.cache_resource to reuse the client across sessions.
    """
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
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

