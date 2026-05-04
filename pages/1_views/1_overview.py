import streamlit as st
import pandas as pd

from models.exposures.spendee._exp_transactions import exp_transactions
from models.metrics.spendee._metric_expenses import metric_expenses

from helpers.charts import (
    bar_chart_by_category,
    bar_chart_by_budget,
    render_transactions_tabbed_chart
)
from helpers.misc import setup_period_selection, get_wallet_options
from helpers.data_transformations.filtering import filter_by_date_range
from helpers.data_transformations.aggregations import (
    get_current_month_expenses,
    get_current_month_income,
    get_last_month_expenses,
    get_last_month_income,
    get_transactions_by_category_sorted,
    get_transactions_by_labels_sorted
)
from helpers.data_transformations.periods import (
    get_available_periods,
    get_period_dates
)

# 1. Load Data
fct_transactions_df = exp_transactions()

# 2. Header & Metrics
st.title(":material/paid: Spendee Expense Dashboard")
st.caption(f"Data range: {fct_transactions_df['date'].min().date()} to {fct_transactions_df['date'].max().date()}")


st.subheader("Current Month Summary")
m1, m2, m3, m4 = st.columns(4)

# MTD Comparison for primary metric
curr_mtd, last_mtd, pct_change = metric_expenses(fct_transactions_df)
# Keep other monthly totals for context
curr_exp = get_current_month_expenses(fct_transactions_df)
last_exp = get_last_month_expenses(fct_transactions_df)

m1.metric(
    "MTD Expenses vs Last Month", 
    f"${curr_mtd:,.0f}", 
    delta=f"{pct_change:+.1f}%",
    help=f"Compared to ${last_mtd:,.0f} spent by this day last month."
)
m2.metric("Gastos Mes Actual", f"${curr_exp:,.0f}")
m3.metric(
    "Ingreso Mes Actual", 
    f"${get_current_month_income(fct_transactions_df):,.0f}",
    delta=f"${get_current_month_income(fct_transactions_df, wallet='Pasivos'):,.0f} Pasivos",
    delta_color="off",
    delta_arrow="off"
)
m4.metric(
    "Ingreso Mes Pasado", 
    f"${get_last_month_income(fct_transactions_df):,.0f}",
    delta=f"${get_last_month_income(fct_transactions_df, wallet='Pasivos'):,.0f} Pasivos",
    delta_color="off",
    delta_arrow="off"
)

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
    selected_wallets = st.multiselect("Wallets", get_wallet_options(fct_transactions_df, include_all=False))

start_date, end_date = get_period_dates(granularity, period_values[selected_label])

# Helper for inline filtering based on current selection
def get_filtered_data(df, type_filter=None):
    data = filter_by_date_range(df, start_date, end_date)
    if selected_wallets:
        data = data[data["wallet"].isin(selected_wallets)]
    if type_filter:
        data = data[data["type"] == type_filter]
    return data

st.markdown(f"### {end_date.strftime('%B %Y')}")

sel_income = get_filtered_data(fct_transactions_df, "Income")["amount"].sum()
sel_expense = get_filtered_data(fct_transactions_df, "Expense")["amount"].sum()

sc1, sc2, sc3 = st.columns(3)
sc1.metric("Selected Period Income", f"${sel_income:,.0f}")
sc2.metric("Selected Period Expenses", f"${sel_expense:,.0f}")
sc3.metric("Net", f"${sel_income - sel_expense:,.0f}")


# 4. Visualizations
st.subheader("By Category")
t1, t2 = st.tabs(["Expenses", "Income"])

with t1:
    st.altair_chart(bar_chart_by_category(get_filtered_data(fct_transactions_df, "Expense")), use_container_width=True)
with t2:
    st.altair_chart(bar_chart_by_category(get_filtered_data(fct_transactions_df, "Income")), use_container_width=True)

st.divider()

st.subheader("By Budget")
st.altair_chart(bar_chart_by_budget(get_filtered_data(fct_transactions_df, "Expense")), use_container_width=True)

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







