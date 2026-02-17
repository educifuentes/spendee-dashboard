import streamlit as st

from models.marts.bi_transactions import bi_transactions

import tests.validate_transactions as validate_transactions


st.header("Validations")


df_transactions = bi_transactions()

validate_transactions.validate_transactions(df_transactions)
