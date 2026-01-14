import streamlit as st
from src.data_preparation import load_transactions
from src.utils import format_currency_columns

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

st.dataframe(
    income_df[selected_columns],
    column_config={
        "date": st.column_config.DateColumn("Date"),
        "category": st.column_config.MultiselectColumn("Category"),
        "amount": st.column_config.NumberColumn(
            "Amount",
            format="%.0f",
        )
    },
    hide_index=True,
    width="stretch"
)
