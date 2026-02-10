import streamlit as st
import pandas as pd
from src.data_preparation import load_transactions
from src.utils import st_dataframe_helper

# Page setup
st.set_page_config(page_title="Search Transactions", page_icon=":material/search:")

st.title("Search Transactions")

# Load data
df = load_transactions()

# Search Input
search_term = st.text_input("Search in notes", placeholder="Type to search...")

# Filter Logic
if search_term:
    # Case-insensitive search in 'note' column, handling NaNs
    filtered_df = df[df["note"].str.contains(search_term, case=False, na=False)]
else:
    filtered_df = df

# Select Columns
columns_to_show = ["category", "note", "date", "label", "amount"]

# Display Dataframe
st_dataframe_helper(
    filtered_df,
    selected_columns=columns_to_show,
    date_columns=["date"],
    currency_columns=["amount"],
    use_container_width=True
)