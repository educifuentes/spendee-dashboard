import streamlit as st
import pandas as pd

from models.marts._fct_transactions import fct_transactions

from utilities.misc import st_dataframe_helper

from models.marts.pivot_tables._pivot_income_month import render_income_pivot_table

df = fct_transactions()

st.title(":material/inventory_2: Income Report")

income_df = render_income_pivot_table(df)

st.divider()

st.subheader("Transaction Details")
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

