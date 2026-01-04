"""
Upload Spendee CSV and sync to Supabase database.
"""
import pandas as pd
import streamlit as st

from utils.clean import add_record_hash, load_budgets
from utils.db import get_supabase


def clean_spendee_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean a Spendee DataFrame (same logic as clean_transactions but for in-memory DataFrame).
    
    Args:
        df: Raw DataFrame from Spendee CSV
        
    Returns:
        Cleaned DataFrame with record_hash
    """
    df = df.copy()
    
    # Rename columns: 'Category name' -> 'category' and lowercase all
    df.columns = df.columns.str.lower()
    df = df.rename(columns={"category name": "category"})
    
    # Convert amount to absolute values
    df["amount"] = df["amount"].abs()
    
    # Convert date to datetime
    df["date"] = pd.to_datetime(df["date"])
    
    # Load budget mappings
    budgets = load_budgets()
    
    # Add budget column by mapping from category
    df["budget"] = df["category"].map(budgets).fillna("Otros")
    
    # Filter to only expenses
    df = df[df["type"].str.lower() == "expense"].copy()
    
    # Drop author column
    if "author" in df.columns:
        df = df.drop(columns=["author"])
    
    # Add record hash for duplicate detection
    df = add_record_hash(df)
    
    return df


@st.cache_data(ttl=300)
def get_existing_hashes() -> set:
    """Get all existing record_hashes from Supabase."""
    supabase = get_supabase()
    response = supabase.table("transactions").select("record_hash").execute()
    return {row["record_hash"] for row in response.data if row.get("record_hash")}


st.title("📤 Upload Data")
st.write("Go to Spendee App and then Settings -> Advanced -> Export")

uploaded_file = st.file_uploader("Choose CSV file", type="csv", key="csv_uploader")

if uploaded_file is not None:
    try:
        # Read CSV - reset file pointer if needed
        uploaded_file.seek(0)
        df_raw = pd.read_csv(uploaded_file)
        
        # Clean the dataframe
        with st.spinner("Cleaning data..."):
            df_cleaned = clean_spendee_df(df_raw)
        
        st.metric("Cleaned rows", len(df_cleaned))
        
        # Get existing hashes
        with st.spinner("Checking for duplicates..."):
            existing_hashes = get_existing_hashes()
        
        # Filter to only new records
        new_transactions = df_cleaned[~df_cleaned["record_hash"].isin(existing_hashes)].copy()
        
        st.metric("New records to upload", len(new_transactions))
        
        if len(new_transactions) == 0:
            st.info("No new records to upload. All records already exist in the database.")
            if st.button("Start over"):
                st.rerun()
        else:
            # Preview
            st.subheader("Preview (first 20 rows)")
            st.dataframe(new_transactions.head(20), width='stretch')
            
            # Convert to dict for Supabase
            records = new_transactions.to_dict("records")
            
            # Upsert to Supabase
            if st.button("Upload to Database", type="primary"):
                with st.spinner("Uploading to Supabase..."):
                    try:
                        supabase = get_supabase()
                        # Convert datetime columns to strings and handle NaN values for JSON serialization
                        for record in records:
                            for key, value in record.items():
                                # Convert datetime to ISO format string
                                if isinstance(value, pd.Timestamp):
                                    if pd.notna(value):
                                        record[key] = value.isoformat()
                                    else:
                                        record[key] = None
                                # Convert NaN values to None (becomes null in JSON)
                                elif pd.isna(value):
                                    record[key] = None
                        
                        response = supabase.table("transactions").upsert(
                            records,
                            on_conflict="record_hash"
                        ).execute()
                        
                        rows_upserted = len(records)
                        st.success(f"✅ Successfully uploaded {rows_upserted} new records!")
                        
                        # Clear cache and rerun
                        st.cache_data.clear()
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error uploading to database: {str(e)}")
            
            if st.button("Cancel"):
                st.rerun()
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        if st.button("Try again"):
            st.rerun()



