import streamlit as st

from models.marts.bi_transactions import bi_transactions

from utilities.misc import st_dataframe_helper

df = bi_transactions()

st.title(":material/receipt_long: Top 50 Expenses")

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

