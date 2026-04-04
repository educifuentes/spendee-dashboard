import streamlit as st

from models.exposures.spendee._exp_transactions import exp_transactions

import tests.validate_transactions as validate_transactions


st.header("Validations")


df_transactions = exp_transactions()

validate_transactions.validate_transactions(df_transactions)
