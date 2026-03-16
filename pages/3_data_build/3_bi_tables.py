import streamlit as st

from models.spendee.marts.bi_transactions import bi_transactions

from utilities.ui_components.render_model import render_model_ui

st.title("Bi Tables")

st.header("Bi Transactions")
df = bi_transactions()
render_model_ui(df)

