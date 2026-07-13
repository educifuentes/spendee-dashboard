import streamlit as st

st.set_page_config(initial_sidebar_state="collapsed")
pages = {
    "Reports": [st.Page(lambda: st.write("P1"), title="P1"), st.Page(lambda: st.write("P2"), title="P2")]
}
st.write("THIS IS A NAVBAR")
pg = st.navigation(pages, position="hidden")
pg.run()
