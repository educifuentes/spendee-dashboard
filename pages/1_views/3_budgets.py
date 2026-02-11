import streamlit as st

from datetime import datetime
from src.data_preparation import load_transactions

from utilities.transforms import get_expenses_by_budget_month
from src.charts import chart_expenses_by_budget_month


# Page configuration
st.set_page_config(
    page_title="Budgets - Spendee Dashboard",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Budgets")

# Load data
df = load_transactions()

# Period filter in main container
with st.container():
    st.header("Filters")
    period_filter = st.selectbox(
        "Period",
        options=["Last 6 months", "Last 12 months", "All months"],
        index=1  # Default to "Last 12 months"
    )

# Calculate date range based on filter
now = datetime.now()
if period_filter == "Last 6 months":
    # Go back 6 months from current month
    if now.month <= 6:
        start_date = datetime(now.year - 1, now.month + 6, 1)
    else:
        start_date = datetime(now.year, now.month - 6, 1)
    end_date = now
elif period_filter == "Last 12 months":
    # Go back 12 months from current month
    if now.month == 12:
        start_date = datetime(now.year, 1, 1)
    else:
        start_date = datetime(now.year - 1, now.month + 1, 1)
    end_date = now
else:  # All months
    start_date = None
    end_date = None

# Get expenses by budget and month
budget_data = get_expenses_by_budget_month(df, start_date, end_date)

if not budget_data.empty:
    # Display chart
    chart = chart_expenses_by_budget_month(budget_data)
    st.altair_chart(chart, width='stretch')
    
    # Optional: Show summary table
    with st.expander("View Data"):
        # Create month label for display
        budget_data_display = budget_data.copy()
        budget_data_display["month_label"] = budget_data_display["date"].dt.strftime("%Y-%m")
        budget_data_display = format_currency_columns(budget_data_display, "CLP")
        summary = budget_data_display.pivot_table(
            index="budget",
            columns="month_label",
            values="amount",
            aggfunc="sum",
            fill_value=0
        )
        st.dataframe(summary, width='stretch')
else:
    st.info("No data available for the selected period.")

