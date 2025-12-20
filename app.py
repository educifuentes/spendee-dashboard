"""
Streamlit BI Dashboard for Spendee Expenses
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from utils.db import load_transactions
from utils.transforms import (
    filter_by_date_range,
    filter_by_category,
    filter_by_label,
    get_current_month_expenses,
    get_last_month_expenses,
    get_expenses_by_category,
    get_expenses_by_month,
    get_top_transactions
)
from utils.charts import (
    chart_expenses_by_category,
    chart_expenses_by_month,
    chart_top_transactions
)


# Page configuration
st.set_page_config(
    page_title="Spendee Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data from Supabase
df = load_transactions()

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter (default: current month)
now = datetime.now()
current_month_start = datetime(now.year, now.month, 1)
current_month_end = now

# Get date range from dataframe
min_date = df["date"].min().date()
max_date = df["date"].max().date()

# Ensure default dates don't exceed dataframe range
default_start = min(max(current_month_start.date(), min_date), max_date)
default_end = min(max(current_month_end.date(), min_date), max_date)

start_date = st.sidebar.date_input(
    "Start Date",
    value=default_start,
    min_value=min_date,
    max_value=max_date
)

end_date = st.sidebar.date_input(
    "End Date",
    value=default_end,
    min_value=min_date,
    max_value=max_date
)

# Granularity selector
granularity = st.sidebar.selectbox(
    "Granularity",
    options=["Month", "Week", "Year"],
    index=0
)

# Category filter
all_categories = sorted(df["category"].unique())
selected_categories = st.sidebar.multiselect(
    "Category",
    options=all_categories,
    default=[]
)

# Label filter
all_labels = set()
for labels_str in df["labels"].dropna():
    if labels_str:
        all_labels.update([l.strip() for l in str(labels_str).split(",")])
all_labels = sorted([l for l in all_labels if l])

selected_labels = st.sidebar.multiselect(
    "Label",
    options=all_labels,
    default=[]
)

# Apply filters
filtered_df = df.copy()
filtered_df = filter_by_date_range(filtered_df, pd.Timestamp(start_date), pd.Timestamp(end_date))
if selected_categories:
    filtered_df = filter_by_category(filtered_df, selected_categories)
if selected_labels:
    filtered_df = filter_by_label(filtered_df, selected_labels)

# Main content
st.title("💰 Spendee Expense Dashboard")

# KPI Panel
st.header("Key Performance Indicators")

col1, col2 = st.columns(2)

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

# Charts section
st.header("Visualizations")

# Chart 1: Expenses by Category (Selected Period)
st.subheader("Expenses by Category (Selected Period)")
category_data = get_expenses_by_category(filtered_df, pd.Timestamp(start_date), pd.Timestamp(end_date))
if not category_data.empty:
    chart1 = chart_expenses_by_category(category_data)
    st.altair_chart(chart1, use_container_width=True)
else:
    st.info("No data available for the selected period and filters.")

# Chart 2: Expenses by Month (Current Year)
st.subheader("Expenses by Month (Current Year)")
monthly_data = get_expenses_by_month(df, year=now.year)
if not monthly_data.empty:
    chart2 = chart_expenses_by_month(monthly_data)
    st.altair_chart(chart2, use_container_width=True)
else:
    st.info("No data available for the current year.")

# Chart 3: Top 10 Transactions (Current Month)
st.subheader("Top 10 Transactions (Current Month)")
top_transactions = get_top_transactions(df, n=10, year=now.year, month=now.month)
if not top_transactions.empty:
    chart3 = chart_top_transactions(top_transactions)
    st.altair_chart(chart3, use_container_width=True)
else:
    st.info("No transactions available for the current month.")

