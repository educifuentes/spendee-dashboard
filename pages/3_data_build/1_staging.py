import streamlit as st

from models.staging._stg_spendee__transactions import stg_spendee__transactions
from models.marts.cloud_sql._stg_cloud_sql__transactions import stg_cloud_sql__transactions

from utilities.ui_components.render_model import render_model_ui

st.title("Staging")

st.header("Stg Spendee Transactions")
df = stg_spendee__transactions()
render_model_ui(df)

st.header("Stg Cloud SQL Transactions")
df_google = stg_cloud_sql__transactions()
render_model_ui(df_google)