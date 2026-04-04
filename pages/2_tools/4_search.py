import streamlit as st

from models.exposures.spendee._exp_transactions import exp_transactions

from helpers.misc import st_dataframe_helper

# Page setup
st.set_page_config(page_title="Search Transactions", page_icon=":material/search:")

st.title("Search Transactions")

# Load data
df = exp_transactions()

# Search Inputs
col1, col2 = st.columns(2)
with col1:
    search_term = st.text_input("Search in notes", placeholder="Type to search notes...")
with col2:
    hash_search = st.text_input("Search by hash", placeholder="Paste hash here...")

# Filter Logic
filtered_df = df
if search_term:
    filtered_df = filtered_df[filtered_df["note"].str.contains(search_term, case=False, na=False)]
if hash_search:
    # Exact or partial match for record_hash
    filtered_df = filtered_df[filtered_df["record_hash"].str.contains(hash_search, case=False, na=False)]

# Select Columns
columns_to_show = ["record_hash", "category", "note", "date", "label", "amount", "amount_universal_clp", "wallet"]

# Display Dataframe
st_dataframe_helper(
    filtered_df,
    selected_columns=columns_to_show,
    date_columns=["date"],
    currency_columns=["amount"],
    use_container_width=True
)