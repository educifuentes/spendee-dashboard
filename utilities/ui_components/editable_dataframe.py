import streamlit as st
import pandas as pd
from utilities.data_connection_cloud_sql import (
    update_transaction, 
    delete_transaction,
    load_transactions
)

def editable_transactions_dataframe(df: pd.DataFrame, key: str):
    """
    Displays a st.data_editor for a transactions dataframe and handles 
    updates & deletions directly to Cloud SQL.
    Returns the edited dataframe.
    """
    if df.empty:
        st.dataframe(df, use_container_width=True)
        return df

    # Prepare for Data Editor
    display_cols = ["id", "date", "category", "labels", "note", "type", "amount", "currency", "amount_universal_clp", "budget", "wallet"]
    # Filter columns if they exist
    valid_cols = [c for c in display_cols if c in df.columns]
    
    # We want to show only specific columns but we NEED 'id' available to update
    if "id" not in valid_cols and "id" in df.columns:
        valid_cols = ["id"] + valid_cols

    editor_df = df[valid_cols].copy()

    # Configuration for columns
    column_config = {
        "id": None, # Hide ID column
        "date": st.column_config.DatetimeColumn("Date", format="DD/MM/YYYY", disabled=False),
        "category": st.column_config.TextColumn("Category", disabled=False),
        "labels": st.column_config.TextColumn("Labels", disabled=False),
        "note": st.column_config.TextColumn("Note", disabled=False),
        "type": st.column_config.TextColumn("Type", disabled=False),
        "amount": st.column_config.NumberColumn("Amount", format="%.2f", disabled=False),
        "currency": st.column_config.TextColumn("Currency", disabled=False),
        "amount_universal_clp": st.column_config.NumberColumn("Amount (CLP)", disabled=True),
        "budget": st.column_config.TextColumn("Budget", disabled=True),
        "wallet": st.column_config.TextColumn("Wallet", disabled=False),
    }

    # --- Data Editor ---
    edited_data = st.data_editor(
        editor_df,
        column_config=column_config,
        num_rows="dynamic", # Allow add/delete (we only implement delete logic for now)
        use_container_width=True,
        key=key,
        hide_index=True
    )

    # --- Handle Updates via Session State ---
    if st.session_state.get(key):
        changes = st.session_state[key]
        
        # 1. Handle Deletes
        if changes.get("deleted_rows"):
            deleted_indices = changes["deleted_rows"]
            for idx in deleted_indices:
                try:
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
                    row_type = editor_df.iloc[idx].get("type", None)
                    current_amount = editor_df.iloc[idx].get("amount", 0)
                    
                    # Filter out derived columns that shouldn't be updated
                    valid_updates = {k: v for k, v in new_values.items() if k not in ["amount_universal_clp", "budget"]}
                    
                    # Ensure the amount stored in DB correctly reflects the expense/income sign
                    if "amount" in valid_updates or "type" in valid_updates:
                        new_type = valid_updates.get("type", row_type)
                        # Get the absolute amount (either the new edited amount, or the current one)
                        unsigned_amount = abs(float(valid_updates.get("amount", current_amount)))
                        
                        if new_type == "Expense":
                            valid_updates["amount"] = -unsigned_amount
                        elif new_type: # Income, Transfer, etc.
                            valid_updates["amount"] = unsigned_amount
                    
                    if valid_updates:
                        update_transaction(row_id, valid_updates)
                        st.toast(f"Updated transaction {row_id}")
                
                except Exception as e:
                    st.error(f"Error updating row {idx}: {e}")

            # Clear cache to reflect changes
            load_transactions.clear()
            st.rerun()
            
    return edited_data
