import streamlit as st

st.set_page_config(initial_sidebar_state="expanded")
p1 = st.Page(lambda: st.write("P1"), title="P1")
try:
    pg = st.navigation([p1], position="top")
    print("TOP_SUPPORTED")
except Exception as e:
    print(f"ERROR: {e}")
