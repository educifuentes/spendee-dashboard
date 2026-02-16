"""
Upload Spendee CSV and sync to Cloud SQL database.
"""
import pandas as pd
import streamlit as st
import sys
import os
from utilities.ui_components.icons import ICONS

# Ensure scripts folder is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.append(project_root)

from utilities.data_transformations.spendee_clean import add_spendee_record_hash as add_record_hash, load_budgets
from scripts.add_new_transactions import get_existing_hashes, insert_new_transactions

def clean_raw_spendee_csv(df: pd.DataFrame) -> pd.DataFrame:
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
def get_cached_existing_hashes() -> set:
    """Wrapper to cache existing hashes from Cloud SQL."""
    return get_existing_hashes()


st.title(f"{ICONS['upload']} Upload Data to Cloud SQL")
st.write("Go to Spendee App and then Settings -> Advanced -> Export")

uploaded_file = st.file_uploader("Choose CSV file", type="csv", key="csv_uploader")

if uploaded_file is not None:
    try:
        # Read CSV - reset file pointer if needed
        uploaded_file.seek(0)
        df_raw = pd.read_csv(uploaded_file)
        
        # Clean the dataframe
        with st.spinner("Cleaning data..."):
            df_cleaned = clean_raw_spendee_csv(df_raw)
        
        st.metric("Cleaned rows", len(df_cleaned))
        
        # Get existing hashes
        with st.spinner("Checking for duplicates (querying Cloud SQL)..."):
            existing_hashes = get_cached_existing_hashes()
        
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
            
            # Insert to SQL
            if st.button("Upload to Database", type="primary"):
                with st.spinner("Uploading to Cloud SQL..."):
                    try:
                        rows_inserted = insert_new_transactions(new_transactions)
                        
                        st.success(f"✅ Successfully uploaded {rows_inserted} new records!")
                        
                        # Clear cache and rerun
                        st.cache_data.clear()
                        # Optional: rerun to reset state
                        # st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error uploading to database: {str(e)}")
            
            if st.button("Cancel"):
                st.rerun()
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        if st.button("Try again"):
            st.rerun()



