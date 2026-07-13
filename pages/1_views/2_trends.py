import streamlit as st

import pandas as pd

from models.exposures.spendee._exp_transactions import exp_transactions

from helpers.charts import (
   render_transactions_tabbed_chart
)




df = exp_transactions()

# last 5 months
df = df[df["date"] >= df["date"].max() - pd.Timedelta(days=6 * 30)]

st.header("Tendencias")
st.markdown("Últimos 6 meses")
st.info("Rango de datos es desde " + df["date"].min().strftime("%Y-%m-%d") + " hasta " + df["date"].max().strftime("%Y-%m-%d"))



granularity = st.selectbox(
    "Granularidad",
    options=["Month", "Week", "Year"],
    format_func=lambda x: {"Month": "Mes", "Week": "Semana", "Year": "Año"}[x],
    index=0,
)
# ------------------------------------------
# 4. Visualizations
# ------------------------------------------
# Chart 1: Transactions bar side by side
render_transactions_tabbed_chart(df, granularity)