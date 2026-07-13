import streamlit as st

from models.exposures.spendee._exp_transactions import exp_transactions

from helpers.misc import st_dataframe_helper

df = exp_transactions()

st.title(":material/receipt_long: Top 50 Gastos")

expenses_df = df[df["type"] == "Expense"]
top_50_expenses = expenses_df.sort_values("amount", ascending=False).head(50)

st_dataframe_helper(
    top_50_expenses,
    selected_columns=[
        "date",
        "amount",
        "currency",
        "category",
        "note",
        "labels"
    ],
    date_columns=["date"],
    multiselect_columns=["category"]
)

