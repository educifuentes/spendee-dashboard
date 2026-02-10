import streamlit as st

from models.marts._fct_transactions import fct_transactions

from utilities.ui_components.render_model import render_model_ui

st.title("Marts")

st.header("Fct Transactions")
df = fct_transactions()
render_model_ui(df)

