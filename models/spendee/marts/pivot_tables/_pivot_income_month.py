import streamlit as st
import pandas as pd

def render_income_pivot_table(df):
    """
    Filters income data and renders a pivot table of income by month and category.
    """
    income_df = df[(df["type"] == "Income")]

    # Pivot table: Months vs Category
    st.subheader("Income Summary by Category")

    categories_to_drop = ["Insurance Payout", "Refund", "Salary", "Extra Income", "Gifts", "Loan"]
    income_df = income_df[~income_df["category"].isin(categories_to_drop)]

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
        # Ensure only existing columns are used
        cols_to_use = [col for col in ordered_columns if col in income_pivot.columns]
        income_pivot = income_pivot[cols_to_use]

        # only data from 2025 onwards
        income_pivot = income_pivot[income_pivot.index >= "2025-01-01"]

        # Format and display
        st.dataframe(
            income_pivot.style.format("${:,.0f}"),
            use_container_width=True
        )
    else:
        st.info("No income data available.")
    
    return income_df