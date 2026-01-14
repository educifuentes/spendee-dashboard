"""
Data Viewer page - Display and filter transactions dataframe.
"""
import pandas as pd
import streamlit as st
from src.data_preparation import load_transactions
from src.utils import filter_dataframe


# Page content
st.title("📊 Data Viewer")

# Load data
df = load_transactions()
df.sort_values("date", ascending=False, inplace=True)

st.write(f"**Total transactions:** {len(df)}")
if "date" in df.columns and len(df) > 0:
    st.write(f"**Date range:** {df['date'].min().date()} to {df['date'].max().date()}")

# Display filtered dataframe
filtered_df = filter_dataframe(df)

st.write(f"**Filtered transactions:** {len(filtered_df)}")
st.dataframe(filtered_df, width='stretch')

