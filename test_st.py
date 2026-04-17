import streamlit as st
import pandas as pd

df = pd.DataFrame({"Monto": [1000, 2000000]})

st.dataframe(df, column_config={
    "Monto": st.column_config.NumberColumn("Monto", format="$ %d"),
    "Monto 2": st.column_config.NumberColumn("Monto 2", format="$ %'d"),
    "Monto 3": st.column_config.NumberColumn("Monto 3", format="$ %d")
})
