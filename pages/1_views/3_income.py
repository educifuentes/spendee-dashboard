import streamlit as st
import pandas as pd

from models.marts._fct_transactions import fct_transactions

from utilities.misc import st_dataframe_helper

df = fct_transactions()

income_df = df[(df["type"] == "Income")]


st.title(":material/inventory_2: Income Report")

# Pivot table: Months vs Category
st.subheader("Income Summary by Category")

categories_to_drop = ["Insurance Payout", "Refund", "Salary", "Extra Income", "Gifts", "Loan"]


if not income_df.empty:
    income_pivot = income_df.pivot_table(
        index="month",
        columns="category",
        values="amount",
        aggfunc="sum",
        fill_value=0
    ).sort_index(ascending=False)
    
    # Remove columns that have always 0
    income_pivot = income_pivot.loc[:, (income_pivot != 0).any(axis=0)]

    
    # Add Total column
    income_pivot['Total'] = income_pivot.sum(axis=1)
    
    ordered_columns = ['Consultoria BI', 'Servicios Foto', 'Sale', 'Rental Apartment', 'Total']
    income_pivot = income_pivot[ordered_columns]

    # only data from 2025 onwards
    income_pivot = income_pivot[income_pivot.index >= "2025-01-01"]

    # Format and display
    st.dataframe(
        income_pivot.style.format("${:,.0f}"),
        use_container_width=True
    )
else:
    st.info("No income data available.")

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

