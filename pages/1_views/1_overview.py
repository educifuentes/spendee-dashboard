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
from utilities.charts import (
    bar_chart_by_category,
    bar_chart_transactions_by_type,
    render_transactions_tabbed_chart
)
from utilities.misc import setup_period_selection, get_wallet_options



# Load data from Supabase
fct_transactions_df = fct_transactions()

# heaader

st.title(":material/paid: Spendee Expense Dashboard")

st.write("Data range is from " + fct_transactions_df["date"].min().strftime("%Y-%m-%d") + " to " + fct_transactions_df["date"].max().strftime("%Y-%m-%d"))


# ------------------------------------------
# 1. Metrics Panel
# ------------------------------------------

col1, col2, col3, col4 = st.columns(4)

# Current month expenses with percentage change
current_month_total = get_current_month_expenses(fct_transactions_df)
last_month_total = get_last_month_expenses(fct_transactions_df)

if last_month_total > 0:
    pct_change = ((current_month_total - last_month_total) / last_month_total) * 100
    delta = f"{pct_change:+.1f}%"
else:
    delta = "N/A"

col1.metric(
    "Current Month Expenses",
    f"${current_month_total:,.0f}",
    delta=delta
)

col2.metric(
    "Last Month Expenses",
    f"${last_month_total:,.0f}"
)

col3.metric(
    "Current Month Income",
    f"${get_current_month_income(fct_transactions_df):,.0f}"
)

col4.metric(
    "Last Month Income",
    f"${get_last_month_income(fct_transactions_df):,.0f}"
)


# ------------------------------------------
# 2. Period Selection Logic
# ------------------------------------------

granularity_key = "granularity"
selected_period_key = "selected_period_label"

granularity, selected_period_label, period_options, period_values, default_index = setup_period_selection(
    fct_transactions_df,
    get_available_periods,
    granularity_key=granularity_key,
    selected_period_key=selected_period_key
)

# Show title (uses session_state value)
st.title(f"{selected_period_label} ")

# Period selector filters UI


wallet_options = get_wallet_options(fct_transactions_df)

col1, col2, col3 = st.columns(3, gap="medium", width=800)

with col1:
    granularity = st.selectbox(
        "Period",
        options=["Month", "Week", "Year"],
        index=0,
        key=granularity_key,
    )

with col2:
    selected_period_label = st.selectbox(
        granularity,
        options=period_options,
        index=default_index,
        key=selected_period_key
    )
with col3:
    selected_wallet = st.selectbox(
        "Wallet",
        options= wallet_options,
        index=0,
    )

# Recalculate start and end dates from selected period
selected_period_value = period_values[selected_period_label]

start_date, end_date = get_period_dates(granularity, selected_period_value)

# ------------------------------------------
# 3. Data Filtering
# ------------------------------------------

# Re-apply filters to dataframe with updated dates
filtered_df = fct_transactions_df.copy()
filtered_df = filter_by_date_range(filtered_df, start_date, end_date)

if selected_wallet != "All":
    filtered_df = filtered_df[filtered_df["wallet"] == selected_wallet]

expenses_df = filtered_df[filtered_df["type"] == "Expense"]
income_df = filtered_df[filtered_df["type"] == "Income"]



# Chart 3: Tables

col1, col2 = st.columns(2)

with col1:
    st.subheader("Expenses by Category")
    st.table(get_transactions_by_category_sorted(expenses_df))
with col2:
    st.subheader("Income by Category")
    st.table(get_transactions_by_category_sorted(income_df))

col1, col2 = st.columns(2)

with col1:
    st.subheader("Expenses by Label")
    st.table(get_transactions_by_labels_sorted(expenses_df))
with col2:
    st.subheader("Income by Label")
    st.table(get_transactions_by_labels_sorted(income_df))

# ------------------------------------------
# 4. Visualizations
# ------------------------------------------
# Chart 1: Transactions bar side by side
render_transactions_tabbed_chart(filtered_df, granularity)


# Chart 2: Expenses by Category
st.subheader("By Category")

tab1, tab2 = st.tabs(["Expenses", "Income"])

with tab1:
    st.subheader("Expenses by Category")
    st.altair_chart(bar_chart_by_category(expenses_df), width='stretch')
with tab2:
    st.subheader("Income by Category")
    st.altair_chart(bar_chart_by_category(income_df), width='stretch')


