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

st.markdown("[Ir a Gsheets](https://docs.google.com/spreadsheets/d/1R6KyFinqSIIXxHEb0vr4-DXy8XsPpXEgBR9HGZ51mms/edit?gid=1953366319#gid=1953366319)")

# Calculate metrics from "monto" based on "status"
sum_done = df_ingresos_proy.loc[df_ingresos_proy['status'].str.lower().str.strip() == 'done', 'monto'].sum()
sum_pending = df_ingresos_proy.loc[df_ingresos_proy['status'].str.lower().str.strip() == 'pending', 'monto'].sum()

total_monto = df_ingresos_proy['monto'].sum()
distinct_months = 1
if 'date' in df_ingresos_proy.columns:
    dates_converted = pd.to_datetime(df_ingresos_proy['date'], errors='coerce')
    months_count = dates_converted.dropna().dt.to_period('M').nunique()
    if months_count > 0:
        distinct_months = months_count

avg_monto_per_month = total_monto / distinct_months

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total", f"${total_monto:,.0f}")
with col2:
    st.metric("Total Done", f"${sum_done:,.0f}")
with col3:
    st.metric("Total Pending", f"${sum_pending:,.0f}")
with col4:
    st.metric("Avg / Month", f"${avg_monto_per_month:,.0f}")

# Display dataframe of ingresos_proyectados
def append_subtotal(df):
    df = df.copy()
    if df.empty:
        return df
    subtotal = pd.Series(index=df.columns, dtype='object')
    if 'status' in df.columns:
        subtotal['status'] = 'SUBTOTAL'
    for col in ["monto", "monto bruto", "deposito"]:
        if col in df.columns:
            subtotal[col] = df[col].sum()
    return pd.concat([df, pd.DataFrame([subtotal])], ignore_index=True)

def format_currency_cols(df):
    df_fmt = df.copy()
    for col in ["monto", "monto bruto", "deposito"]:
        if col in df_fmt.columns:
            df_fmt[col] = pd.to_numeric(df_fmt[col], errors='coerce')
            df_fmt[col] = df_fmt[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "")
    return df_fmt

st.markdown("##### Done")
df_done = df_ingresos_proy[df_ingresos_proy['status'].str.lower().str.strip() == 'done'].copy()
df_done = df_done.sort_values("date", ascending=False) if "date" in df_done.columns else df_done
df_done = append_subtotal(df_done)

st_dataframe_helper(
    format_currency_cols(df_done),
    selected_columns=df_done.columns.tolist(),
    date_columns=["date"] if "date" in df_done.columns else [],
    currency_columns=[], # Removed since we formatted them as strings
    multiselect_columns=["status", "area", "cliente"]
)

st.markdown("##### Pending")
df_pending = df_ingresos_proy[df_ingresos_proy['status'].str.lower().str.strip() != 'done'].copy()
df_pending = df_pending.sort_values("date", ascending=False) if "date" in df_pending.columns else df_pending
df_pending = append_subtotal(df_pending)

st_dataframe_helper(
    format_currency_cols(df_pending),
    selected_columns=df_pending.columns.tolist(),
    date_columns=["date"] if "date" in df_pending.columns else [],
    currency_columns=[], # Removed since we formatted them as strings
    multiselect_columns=["status", "area", "cliente"]
)

st.divider()

# --- Ingresos Section ---
st.subheader("Spendee Income")

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

