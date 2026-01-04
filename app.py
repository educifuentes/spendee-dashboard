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
    create_period_columns,
    get_current_month_expenses,
    get_current_month_income,
    get_last_month_expenses,
    get_expenses_by_category,
    get_expenses_by_month,
    get_top_transactions,
    get_top_expenses_by_label,
    get_available_periods,
    get_period_dates
)
from utils.charts import (
    chart_expenses_by_category,
    bar_chart_transactions_by_type,
    chart_expenses_by_period,
    chart_top_transactions,
    chart_top_expenses_by_label
)


# ==========================================
# Page Configuration
# ==========================================
st.set_page_config(
    page_title="Spendee Dashboard :material/paid:",
    page_icon=":material/paid:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# Sidebar & Data Loading
# ==========================================
st.sidebar.title("Navigation")

# Load data from Supabase
df = load_transactions()
df = create_period_columns(df)


now = datetime.now()

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

# ==========================================
# Main Dashboard Layout
# ==========================================
st.title(":material/paid: Spendee Expense Dashboard")


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
col1, col2,col3 = st.columns(3)

wallet_options = ["All"] + sorted(df["wallet"].unique().tolist())

with col1:
    granularity = st.selectbox(
        "Period",
        options=["Month", "Week", "Year"],
        index=0,
        key=granularity_key
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
if selected_categories:
    filtered_df = filter_by_category(filtered_df, selected_categories)
if selected_labels:
    filtered_df = filter_by_label(filtered_df, selected_labels)

# ------------------------------------------
# 4. Visualizations
# ------------------------------------------

# Chart 1: Expenses bar

tab1, tab2, tab3 = st.tabs(["Days", "Weeks", "Months"])
with tab1:
    st.altair_chart( bar_chart_transactions_by_type(filtered_df, period="Day"), use_container_width=True)
with tab2:
    st.altair_chart(bar_chart_transactions_by_type(filtered_df, period="Week"), use_container_width=True)
with tab3:
    st.altair_chart(bar_chart_transactions_by_type(filtered_df, period="Month"), use_container_width=True)

# Chart 2: Expenses by Category
st.altair_chart(chart_expenses_by_category(filtered_df), width='stretch')


# tab1, tab2, tab3, tab4 = st.tabs([wallet_options])
# with tab1:
#     filtered_df = filter_by_date_range(df, pd.Timestamp(start_date), pd.Timestamp(end_date))
#     st.altair_chart(chart_expenses_by_category(filtered_df), width='stretch')
# with tab2:
#     filtered_df = filter_by_date_range(df[df["wallet"]==wallet_options[1]], pd.Timestamp(start_date), pd.Timestamp(end_date))
#     st.altair_chart(chart_expenses_by_category(filtered_df), wid  th='stretch')
# with tab3:
#     filtered_df = filter_by_date_range(df[df["wallet"]==wallet_options[2]], pd.Timestamp(start_date), pd.Timestamp(end_date))
#     st.altair_chart(chart_expenses_by_category(filtered_df), width='stretch')  
# with tab4:
#     filtered_df = filter_by_date_range(df[df["wallet"]==wallet_options[3]], pd.Timestamp(start_date), pd.Timestamp(end_date))
#     st.altair_chart(chart_expenses_by_category(filtered_df), width='stretch')


# Chart 2: Top 10 Transactions 

top_transactions = get_top_transactions(df, n=10, year=now.year, month=now.month)
if not top_transactions.empty:
    st.altair_chart( chart_top_transactions(top_transactions), width='stretch')
else:
    st.info("No transactions available for the current month.")

# Chart 3: Top Expenses by Label

top_labels = get_top_expenses_by_label(df, n=10, year=now.year, month=now.month)
if not top_labels.empty:
    chart4 = chart_top_expenses_by_label(top_labels)
    st.altair_chart(chart4, width='stretch')
else:
    st.info("No expenses with labels available for the current month.")
