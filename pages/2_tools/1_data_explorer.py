"""
Data Viewer page - Display and filter transactions dataframe.
"""
import streamlit as st
import pandas as pd

from datetime import date, timedelta
from models.spendee.marts.bi_transactions import bi_transactions
from helpers.data_connection_cloud_sql import (
    update_transaction, 
    delete_transaction,
    load_transactions
)
from helpers.ui_components.dataframe_column_display import dataframe_column_display

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

# --- Data Editor ---
from helpers.ui_components.editable_dataframe import editable_transactions_dataframe

edited_data = editable_transactions_dataframe(filtered_df, key="transaction_editor")
