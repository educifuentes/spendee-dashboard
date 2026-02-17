"""
Data Viewer page - Display and filter transactions dataframe.
"""
import streamlit as st
import pandas as pd

from datetime import date, timedelta
from models.marts.bi_transactions import bi_transactions
from utilities.data_connection_cloud_sql import (
    update_transaction, 
    delete_transaction,
    load_transactions
)
from utilities.ui_components.dataframe_column_display import dataframe_column_display

# Page content
st.title("Data Explorer")

# Load data - computed columns will be read-only
df = bi_transactions()
if "date" in df.columns:
    df = df.sort_values("date", ascending=False)

# --- Date Filter ---
today = date.today()
default_start = today - timedelta(days=30)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    start_date = st.date_input("Start Date", value=default_start, format="YYYY-MM-DD")
with col2:
    end_date = st.date_input("End Date", value=today, format="YYYY-MM-DD")

# Apply Date Filter
filtered_df = df.copy()
mask = (filtered_df['date'].dt.date >= start_date) & (filtered_df['date'].dt.date <= end_date)
filtered_df = filtered_df[mask]

st.markdown(f"**Showing {len(filtered_df)} transactions**")

# Prepare for Data Editor
display_cols = ["id", "date", "category", "labels", "note", "type", "amount", "currency", "amount_universal_clp", "budget"]
# Filter columns if they exist
valid_cols = [c for c in display_cols if c in filtered_df.columns]
editor_df = filtered_df[valid_cols].copy()

# Configuration for columns
column_config = {
    "id": None, # Hide ID column
    "date": st.column_config.DatetimeColumn("Date", format="DD/MM/YYYY", disabled=False),
    "category": st.column_config.TextColumn("Category", disabled=True),
    "labels": st.column_config.TextColumn("Labels", disabled=True), # Or ListColumn if it comes as list
    "note": st.column_config.TextColumn("Note", disabled=False),
    "type": st.column_config.TextColumn("Type", disabled=True),
    "amount": st.column_config.NumberColumn("Amount", format="%.2f", disabled=False),
    "currency": st.column_config.TextColumn("Currency", disabled=True),
    "amount_universal_clp": st.column_config.NumberColumn("Amount (CLP)", disabled=True),
    "budget": st.column_config.TextColumn("Budget", disabled=True),
}

# --- Data Editor ---
edited_data = st.data_editor(
    editor_df,
    column_config=column_config,
    num_rows="dynamic", # Allow add/delete (we only implement delete logic for now)
    use_container_width=True,
    key="transaction_editor",
    hide_index=True
)

# --- Handle Updates via Session State ---
if st.session_state.get("transaction_editor"):
    changes = st.session_state["transaction_editor"]
    
    # 1. Handle Deletes
    if changes.get("deleted_rows"):
        deleted_indices = changes["deleted_rows"]
        for idx in deleted_indices:
            try:
                # Get ID from the original editor_df
                # Note: indices in deleted_rows refer to the dataframe passed to data_editor
                row_id = editor_df.iloc[idx]["id"]
                delete_transaction(row_id)
                st.toast(f"Deleted transaction {row_id}")
            except Exception as e:
                st.error(f"Error deleting row {idx}: {e}")
        
        # Clear cache to reflect changes
        load_transactions.clear()
        st.rerun()

    # 2. Handle Edits
    if changes.get("edited_rows"):
        edited_rows = changes["edited_rows"]
        for idx, new_values in edited_rows.items():
            try:
                row_id = editor_df.iloc[idx]["id"]
                
                # Filter out derived columns that shouldn't be updated
                valid_updates = {k: v for k, v in new_values.items() if k not in ["amount_universal_clp", "budget"]}
                
                if valid_updates:
                    update_transaction(row_id, valid_updates)
                    st.toast(f"Updated transaction {row_id}")
            
            except Exception as e:
                st.error(f"Error updating row {idx}: {e}")

        # Clear cache to reflect changes
        load_transactions.clear()
        st.rerun()
