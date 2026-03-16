import streamlit as st

from models.spendee.staging._stg_spendee__transactions import stg_spendee__transactions

from utilities.ui_components.render_model import render_model_ui

st.title("Staging")

st.header("Stg Spendee Transactions")
st.markdown("### Cloud SQL")
df = stg_spendee__transactions()

render_model_ui(df)