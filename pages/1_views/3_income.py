import streamlit as st
import pandas as pd

from models.exposures.spendee._exp_income_by_month import exp_income_by_month
from models.marts.gsheets._fct_ingresos_proyectados import fct_ingresos_proyectados

from helpers.misc import st_dataframe_helper

# Load Data
df_ingresos_proy = fct_ingresos_proyectados()
income_df = exp_income_by_month()

st.title(":material/inventory_2: Income Report")

# --- Ingresos Proyectados Section ---
st.subheader("Ingresos Proyectados")

# Calculate metrics from "monto" based on "status"
sum_done = df_ingresos_proy.loc[df_ingresos_proy['status'].str.lower().str.strip() == 'done', 'monto'].sum()
sum_pending = df_ingresos_proy.loc[df_ingresos_proy['status'].str.lower().str.strip() == 'pending', 'monto'].sum()

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Done", f"${sum_done:,.0f}")
with col2:
    st.metric("Total Pending", f"${sum_pending:,.0f}")

# Display dataframe of ingresos_proyectados
st_dataframe_helper(
    df_ingresos_proy.sort_values("date", ascending=False) if "date" in df_ingresos_proy.columns else df_ingresos_proy,
    selected_columns=df_ingresos_proy.columns.tolist(),
    date_columns=["date"] if "date" in df_ingresos_proy.columns else [],
    currency_columns=["monto", "monto bruto", "deposito"],
    multiselect_columns=["status", "area", "cliente"]
)

st.divider()

# --- Ingresos Section ---
st.header("Ingresos")
st.subheader("Transaction Details")

st_dataframe_helper(
    income_df,
    selected_columns=[
        "month",
        "amount",
        "amount_universal_clp"
    ],
    date_columns=[],
    currency_columns=["amount", "amount_universal_clp"],
    multiselect_columns=["month"]
)

