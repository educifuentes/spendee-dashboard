import streamlit as st
import pandas as pd

from models.exposures.spendee._exp_transactions import exp_transactions

from models.exposures.spendee._exp_income_by_month import exp_income_by_month
from helpers.misc import st_dataframe_helper


df = exp_transactions()

st.title(":material/inventory_2: Income Report")

income_df = exp_income_by_month(df)

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

