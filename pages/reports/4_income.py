import streamlit as st
from src.data_preparation import load_transactions
from src.utils import st_dataframe_helper

df = load_transactions()

income_df = df[(df["type"] == "Income")]

st.title(":material/inventory_2: Income Report")

selected_columns = [
    "date",
    "amount",
    "currency",
    "category",
    "note",
    "labels"    
]

st_dataframe_helper(
    income_df,
    selected_columns=selected_columns,
    date_columns=["date"],
    currency_columns=["amount"],
    multiselect_columns=["category"]
)

