import streamlit as st

st.set_page_config(initial_sidebar_state="collapsed")

# Inject CSS to position a custom container in the Streamlit top header
st.markdown("""
<style>
    .utilities-container {
        position: fixed;
        top: 0.5rem;
        right: 1rem;
        z-index: 999999;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
</style>
<div class="utilities-container" id="utilities-container">
</div>
""", unsafe_allow_html=True)

pages = {
    "Reports": [st.Page(lambda: st.write("P1"), title="P1"), st.Page(lambda: st.write("P2"), title="P2")]
}
pg = st.navigation(pages, position="top")
pg.run()
