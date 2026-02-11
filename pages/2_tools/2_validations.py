import streamlit as st

import tests.validate_transactions as validate_transactions
from models.marts._fct_transactions import fct_transactions

st.header("Validations")


df_transactions = fct_transactions()

validate_transactions.validate_transactions(df_transactions)
