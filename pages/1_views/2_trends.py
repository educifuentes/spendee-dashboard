import streamlit as st

import pandas as pd

from models.exposures.spendee._exp_transactions import exp_transactions

from helpers.charts import (
   render_transactions_tabbed_chart
)




df = exp_transactions()

# last 5 months
df = df[df["date"] >= df["date"].max() - pd.Timedelta(days=6 * 30)]

st.header("Trends")
st.markdown("Last 6 months")
st.info("Data range is from " + df["date"].min().strftime("%Y-%m-%d") + " to " + df["date"].max().strftime("%Y-%m-%d"))



granularity = st.selectbox(
    "Granularity",
    options=["Month", "Week", "Year"],
    index=0,
)
# ------------------------------------------
# 4. Visualizations
# ------------------------------------------
# Chart 1: Transactions bar side by side
render_transactions_tabbed_chart(df, granularity)