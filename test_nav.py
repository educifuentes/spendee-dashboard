import streamlit as st

st.set_page_config(initial_sidebar_state="expanded")
p1 = st.Page(lambda: st.write("P1"), title="P1")
pg = st.navigation([p1], position="hidden")
print(pg)
