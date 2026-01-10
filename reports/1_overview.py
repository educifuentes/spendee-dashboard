import streamlit as st
import pandas as pd
from datetime import datetime

from src.data_preparation import load_transactions
from src.transforms import (
    filter_by_date_range,
    get_current_month_expenses,
    get_current_month_income,
    get_last_month_expenses,
    get_available_periods,
    get_period_dates,
    get_transactions_by_category_sorted
)
from src.charts import (
    bar_chart_by_category,
    bar_chart_transactions_by_type
)


# ==========================================
# Sidebar & Data Loading
# ==========================================

# Load data from Supabase
df = load_transactions()

now = datetime.now()


# ==========================================
# Main Dashboard Layout
# ==========================================
st.title(":material/paid: Spendee Expense Dashboard")
st.subheader("Overview of your expenses and income")

st.write("Data range is from " + df["date"].min().strftime("%Y-%m-%d") + " to " + df["date"].max().strftime("%Y-%m-%d"))


# ------------------------------------------
# 1. Key Performance Indicators (KPIs)
# ------------------------------------------

col1, col2, col3 = st.columns(3)

# Current month expenses with percentage change
current_month_total = get_current_month_expenses(df)
last_month_total = get_last_month_expenses(df)

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
    f"${get_current_month_income(df):,.0f}"
)


# ------------------------------------------
# 2. Period Selection Logic
# ------------------------------------------

# Period selector filters - calculate period options first
granularity_key = "granularity"
if granularity_key not in st.session_state:
    st.session_state[granularity_key] = "Month"

granularity = st.session_state[granularity_key]
available_periods = get_available_periods(df, granularity)
period_options = [p["period_label"] for p in available_periods]
period_values = {p["period_label"]: p["period_value"] for p in available_periods}

# Get default index for selected period
selected_period_key = "selected_period_label"
if selected_period_key not in st.session_state or st.session_state[selected_period_key] not in period_options:
    if granularity == "Month" and period_options:
        current_period_label = datetime.now().strftime("%B %Y")
        default_index = period_options.index(current_period_label) if current_period_label in period_options else len(period_options) - 1
    elif period_options:
        default_index = len(period_options) - 1
    else:
        default_index = 0
    st.session_state[selected_period_key] = period_options[default_index] if period_options else ""
else:
    default_index = period_options.index(st.session_state[selected_period_key]) if st.session_state[selected_period_key] in period_options else 0

# Show title (uses session_state value)
st.title(f"{st.session_state[selected_period_key]} ")

# Period selector filters UI


wallet_options = ["All"] + sorted(df["wallet"].unique().tolist())

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
filtered_df = df.copy()
filtered_df = filter_by_date_range(filtered_df, start_date, end_date)

if selected_wallet != "All":
    filtered_df = filtered_df[filtered_df["wallet"] == selected_wallet]

expenses_df = filtered_df[filtered_df["type"] == "Expense"].copy()
income_df = filtered_df[filtered_df["type"] == "Income"].copy()

# ------------------------------------------
# 4. Visualizations
# ------------------------------------------

# Chart 1: Transactions bar side by side

# Change first tab to display according to granularity
if granularity == "Month":
    tabs_config = [("Weeks", "Week"), ("Days", "Day"), ("Months", "Month")]
elif granularity == "Year":
    tabs_config = [("Months", "Month"), ("Weeks", "Week"), ("Days", "Day")]
else:
    tabs_config = [("Days", "Day"), ("Weeks", "Week"), ("Months", "Month")]

tabs = st.tabs([t[0] for t in tabs_config])
for tab, (label, period) in zip(tabs, tabs_config):
    with tab:
        st.altair_chart(bar_chart_transactions_by_type(filtered_df, period=period), use_container_width=True)

# Chart 2: Expenses by Category
st.subheader("By Category")

tab1, tab2 = st.tabs(["Expenses", "Income"])

with tab1:
    st.subheader("Expenses by Category")
    st.altair_chart(bar_chart_by_category(expenses_df), width='stretch')
with tab2:
    st.subheader("Income by Category")
    st.altair_chart(bar_chart_by_category(income_df), width='stretch')


# Chart 3: Tables

col1, col2 = st.columns(2)

with col1:
    st.subheader("Expenses by Category")
    st.table(get_transactions_by_category_sorted(expenses_df))
with col2:
    st.subheader("Income by Category")
    st.table(get_transactions_by_category_sorted(income_df))

