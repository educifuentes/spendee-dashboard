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
    chart_expenses_by_period,
    chart_top_transactions
)


# Page configuration
st.set_page_config(
    page_title="Spendee Dashboard :material/paid:",
    page_icon=":material/paid:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("Navigation")

# Load data from Supabase
df = load_transactions()

# Sidebar filters
st.sidebar.header("Filters")

now = datetime.now()

# Filters

# Period selector
granularity = st.sidebar.selectbox(
    "Period",
    options=["Month", "Week", "Year"],
    index=0
)

# Get available periods based on granularity
def get_available_periods(df, period_type):
    """Get available periods from dataframe, formatted and sorted chronologically."""
    df_copy = df.copy()
    
    if period_type == "Month":
        # Group by year-month, format as "Month Year"
        df_copy["period_key"] = df_copy["date"].dt.to_period("M")
        periods = df_copy.groupby("period_key")["date"].first().reset_index()
        periods["period_label"] = periods["period_key"].apply(lambda p: p.strftime("%B %Y"))
        periods["period_value"] = periods["period_key"].astype(str)
    elif period_type == "Week":
        # Group by ISO week, get Monday of the week, format as "Month Day, Year"
        df_copy["year"] = df_copy["date"].dt.isocalendar().year
        df_copy["week"] = df_copy["date"].dt.isocalendar().week
        df_copy["period_key"] = df_copy["year"].astype(str) + "-W" + df_copy["week"].astype(str).str.zfill(2)
        
        # Calculate Monday of each week
        periods = df_copy.groupby("period_key")["date"].first().reset_index()
        periods["monday"] = periods["date"].apply(lambda d: d - pd.Timedelta(days=d.weekday()))
        # Format as "Month Day, Year" (handle day without leading zero)
        periods["period_label"] = periods["monday"].apply(lambda d: f"{d.strftime('%B')} {d.day}, {d.year}")
        periods["period_value"] = periods["period_key"]
    else:  # Year
        df_copy["period_key"] = df_copy["date"].dt.year
        periods = df_copy.groupby("period_key")["date"].first().reset_index()
        periods["period_label"] = periods["period_key"].astype(str)
        periods["period_value"] = periods["period_key"].astype(str)
    
    # Sort chronologically by date
    periods = periods.sort_values("date")
    return periods[["period_label", "period_value"]].to_dict("records")

# Get available periods
available_periods = get_available_periods(df, granularity)
period_options = [p["period_label"] for p in available_periods]
period_values = {p["period_label"]: p["period_value"] for p in available_periods}

# Default to current month
if granularity == "Month" and period_options:
    current_period_label = datetime.now().strftime("%B %Y")
    default_index = period_options.index(current_period_label) if current_period_label in period_options else len(period_options) - 1
elif period_options:
    default_index = len(period_options) - 1
else:
    default_index = 0

# Period selector
selected_period_label = st.sidebar.selectbox(
    granularity,
    options=period_options,
    index=default_index
)

# Calculate start and end dates from selected period
selected_period_value = period_values[selected_period_label]

if granularity == "Month":
    # Parse YYYY-MM format
    year, month = map(int, selected_period_value.split("-"))
    start_date = pd.Timestamp(year=year, month=month, day=1)
    # Get last day of month
    if month == 12:
        end_date = pd.Timestamp(year=year+1, month=1, day=1) - pd.Timedelta(days=1)
    else:
        end_date = pd.Timestamp(year=year, month=month+1, day=1) - pd.Timedelta(days=1)
    end_date = end_date.replace(hour=23, minute=59, second=59)
elif granularity == "Week":
    # Parse YYYY-WXX format, get Monday and Sunday of that week
    year, week = selected_period_value.split("-W")
    year, week = int(year), int(week)
    # Get Monday of the week
    start_date = pd.Timestamp.fromisocalendar(year, week, 1)
    end_date = start_date + pd.Timedelta(days=6, hours=23, minutes=59, seconds=59)
else:  # Year
    year = int(selected_period_value)
    start_date = pd.Timestamp(year=year, month=1, day=1)
    end_date = pd.Timestamp(year=year, month=12, day=31, hour=23, minute=59, second=59)

# Convert to date objects for filtering
start_date = start_date.date()
end_date = end_date.date()



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

# Chart 2: Expenses by Period (Selected Period)
st.subheader(f"Expenses by {granularity} (Selected Period)")
period_data = filtered_df.copy()
if not period_data.empty:
    chart2 = chart_expenses_by_period(period_data, period=granularity)
    st.altair_chart(chart2, use_container_width=True)
else:
    st.info("No data available for the selected period.")

# Chart 3: Top 10 Transactions (Current Month)
st.subheader("Top 10 Transactions (Current Month)")
top_transactions = get_top_transactions(df, n=10, year=now.year, month=now.month)
if not top_transactions.empty:
    chart3 = chart_top_transactions(top_transactions)
    st.altair_chart(chart3, use_container_width=True)
else:
    st.info("No transactions available for the current month.")

