"""
Data Viewer page - Display and filter transactions dataframe.
"""
import streamlit as st
import pandas as pd

from models.marts.bi_transactions import bi_transactions

from utilities.ui_components.dataframe_column_display import dataframe_column_display

# Page content
st.title("Data Explorer")
    
# Load data
df = bi_transactions()

# Ensure date is sorted descending
if "date" in df.columns:
    df = df.sort_values("date", ascending=False)

st.markdown(f"**Data range:** {df['date'].min().date()} to {df['date'].max().date()}")

display_columns = ["date", "category", "labels", "note", "type", "amount", "amount_universal_clp", "budget"]

# Display styled dataframe using utility function
dataframe_column_display(
    df[display_columns],
    currency_cols=["amount", "amount_universal_clp"],
    date_cols=["date"],
    multiselect_cols=["category"],
    selectbox_cols=["labels"]
)
