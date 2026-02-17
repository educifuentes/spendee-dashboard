import streamlit as st

from utilities.data_connection_cloud_sql import load_transactions

from utilities.ui_components.render_model import render_model_ui

st.title("Staging")

st.header("Stg Cloud SQL Transactions")
df_google = load_transactions()
render_model_ui(df_google)