import streamlit as st

from models.marts._fct_transactions import fct_transactions

import tests.validate_transactions as validate_transactions


st.header("Validations")


df_transactions = fct_transactions()

validate_transactions.validate_transactions(df_transactions)
