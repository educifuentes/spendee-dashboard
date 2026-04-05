"""
Upload Spendee CSV and sync to the GCS-hosted SQLite database.
"""
import pandas as pd
import streamlit as st
import sys
import os
from helpers.ui_components.icons import ICONS

# Ensure scripts folder is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

from helpers.data_transformations.spendee_clean import add_spendee_record_hash as add_record_hash
from helpers.data_connection_cloud_sql import (
    get_engine,
    get_latest_transaction_date,
    insert_new_transactions,
)

st.title(f"{ICONS['upload']} Upload Data")
st.write("Go to Spendee App and then Settings -> Advanced -> Export")
st.write("You can upload multiple CSV files at once.")

uploaded_files = st.file_uploader("Choose CSV files", type="csv", accept_multiple_files=True, key="csv_uploader")

if uploaded_files:
    try:
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
        
        df_list = []
        
        with st.spinner("Processing files..."):
            for uploaded_file in uploaded_files:
                uploaded_file.seek(0)
                wallet_df = pd.read_csv(uploaded_file)
                
                # Standardize columns to database schema
                wallet_df = wallet_df.rename(columns=rename_map)
                
                # Only keep columns we care about if extra ones exist
                keep_cols = [c for c in rename_map.values() if c in wallet_df.columns]
                wallet_df = wallet_df[keep_cols]
                
                df_list.append(wallet_df)
                
        if not df_list:
            st.error("No data found in the uploaded files.")
            st.stop()
            
        # Combine all dataframes into one
        df = pd.concat(df_list, ignore_index=True)
        st.metric("Total rows found", len(df))
        
        # Generate the required record_hash for the database
        df = add_record_hash(df)
        
        # Get DB engine and latest date
        with st.spinner("Querying database for latest transactions..."):
            engine = get_engine()
            
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors='coerce')
                
            latest_date = get_latest_transaction_date(engine)
            
            if latest_date is not None:
                st.write(f"Latest transaction in database is from: **{latest_date}**")
                # Align timezones if necessary for comparison
                csv_tz = getattr(df["date"].dt, 'tz', None)
                
                if latest_date.tzinfo is not None and csv_tz is None:
                    df["date"] = df["date"].dt.tz_localize(latest_date.tzinfo)
                elif latest_date.tzinfo is None and csv_tz is not None:
                    df["date"] = df["date"].dt.tz_localize(None)
                    
                new_transactions = df[df["date"] > latest_date].copy()
            else:
                st.write("No existing transactions found or could not fetch latest date. Inserting all rows.")
                new_transactions = df.copy()
                
        st.metric("New records to upload", len(new_transactions))
        
        if new_transactions.empty:
            st.info("No new records to upload. All records already exist in the database.")
            if st.button("Start over"):
                st.rerun()
        else:
            # Preview
            st.subheader("Preview (first 20 rows)")
            st.dataframe(new_transactions.head(20), width='stretch')
            
            # Insert to SQL
            if st.button("Upload to Database", type="primary"):
                with st.spinner("Uploading to database and syncing to GCS..."):
                    try:
                        rows_inserted = insert_new_transactions(new_transactions, engine)
                        
                        st.success(f"✅ Successfully uploaded {rows_inserted} new records!")
                        
                        # Clear cache if any
                        st.cache_data.clear()
                        
                    except Exception as e:
                        st.error(f"Error uploading to database: {str(e)}")
            
            if st.button("Cancel"):
                st.rerun()
                
    except Exception as e:
        st.error(f"Error processing files: {str(e)}")
        if st.button("Try again"):
            st.rerun()


