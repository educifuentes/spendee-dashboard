import streamlit as st
import pandas as pd
from src.data_preparation import load_transactions
from utilities.misc import st_dataframe_helper

df = load_transactions()

income_df = df[(df["type"] == "Income")]

st.title(":material/inventory_2: Income Report")


st_dataframe_helper(
    income_df.sort_values("date", ascending=False),
    selected_columns=[
        "date",
        "amount",
        "currency",
        "category",
        "note",
        "labels"    
    ],
    date_columns=["date"],
    currency_columns=["amount"],
    multiselect_columns=["category"]
)

