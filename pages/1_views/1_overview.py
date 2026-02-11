import streamlit as st
import pandas as pd

from models.marts._fct_transactions import fct_transactions
from utilities.transforms import (
    filter_by_date_range,
    get_current_month_expenses,
    get_current_month_income,
    get_last_month_expenses,
    get_last_month_income,
    get_available_periods,
    get_period_dates,
    get_transactions_by_category_sorted,
    get_transactions_by_labels_sorted
)
from models.marts.metrics.expense_metrics import get_mtd_expense_comparison
from utilities.charts import (
    bar_chart_by_category,
    render_transactions_tabbed_chart
)
from utilities.misc import setup_period_selection, get_wallet_options

# 1. Load Data
fct_transactions_df = fct_transactions()

# 2. Header & Metrics
st.title(":material/paid: Spendee Expense Dashboard")
st.info(f"Data range: {fct_transactions_df['date'].min().date()} to {fct_transactions_df['date'].max().date()}")

m1, m2, m3, m4 = st.columns(4)

# MTD Comparison for primary metric
curr_mtd, last_mtd, pct_change = get_mtd_expense_comparison(fct_transactions_df)

m1.metric(
    "MTD Expenses vs Last Month", 
    f"${curr_mtd:,.0f}", 
    delta=f"{pct_change:+.1f}%",
    help=f"Compared to ${last_mtd:,.0f} spent by this day last month."
)

# Keep other monthly totals for context
curr_exp = get_current_month_expenses(fct_transactions_df)
last_exp = get_last_month_expenses(fct_transactions_df)
m2.metric("Current Month Total", f"${curr_exp:,.0f}")
m3.metric("Current Month Income", f"${get_current_month_income(fct_transactions_df):,.0f}")
m4.metric("Last Month Income", f"${get_last_month_income(fct_transactions_df):,.0f}")

st.divider()

# 3. Filters & Period Selection
granularity, selected_label, period_options, period_values, default_index = setup_period_selection(
    fct_transactions_df, get_available_periods
)

st.title(f"{selected_label}")

c1, c2, c3 = st.columns(3)
with c1:
    granularity = st.selectbox("Period", ["Month", "Week", "Year"], index=0, key="granularity")
with c2:
    selected_label = st.selectbox(granularity, period_options, index=default_index, key="selected_period_label")
with c3:
    selected_wallet = st.selectbox("Wallet", get_wallet_options(fct_transactions_df), index=0)

start_date, end_date = get_period_dates(granularity, period_values[selected_label])

# Helper for inline filtering based on current selection
def get_filtered_data(df, type_filter=None):
    data = filter_by_date_range(df, start_date, end_date)
    if selected_wallet != "All":
        data = data[data["wallet"] == selected_wallet]
    if type_filter:
        data = data[data["type"] == type_filter]
    return data

# 4. Visualizations
st.subheader("By Category")
t1, t2 = st.tabs(["Expenses", "Income"])

with t1:
    st.altair_chart(bar_chart_by_category(get_filtered_data(fct_transactions_df, "Expense")), use_container_width=True)
with t2:
    st.altair_chart(bar_chart_by_category(get_filtered_data(fct_transactions_df, "Income")), use_container_width=True)

st.divider()

# 5. Tables
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Expenses by Category")
    st.table(get_transactions_by_category_sorted(get_filtered_data(fct_transactions_df, "Expense")))
    st.subheader("Expenses by Label")
    st.table(get_transactions_by_labels_sorted(get_filtered_data(fct_transactions_df, "Expense")))

with col_b:
    st.subheader("Income by Category")
    st.table(get_transactions_by_category_sorted(get_filtered_data(fct_transactions_df, "Income")))
    st.subheader("Income by Label")
    st.table(get_transactions_by_labels_sorted(get_filtered_data(fct_transactions_df, "Income")))







