import streamlit as st

st.set_page_config(initial_sidebar_state="collapsed")
pages = {
    "Reports": [st.Page(lambda: st.write("P1"), title="P1"), st.Page(lambda: st.write("P2"), title="P2")],
    "Dev": [st.Page(lambda: st.write("D1"), title="D1")]
}
pg = st.navigation(pages, position="top")
pg.run()
