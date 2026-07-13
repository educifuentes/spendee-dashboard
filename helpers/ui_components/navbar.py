import streamlit as st
from helpers.app_version import get_app_version

def render_custom_navbar():
    # CSS to hide the default sidebar toggle, adjust popovers to look like navbar links,
    # and fix the top padding so the navbar is close to the top edge.
    st.markdown("""
        <style>
            [data-testid="collapsedControl"] {
                display: none;
            }
            div[data-testid="stPopover"] > button {
                background-color: transparent;
                border: 1px solid rgba(250, 250, 250, 0.2);
                font-weight: 600;
            }
            div[data-testid="stPopover"] > button:hover {
                background-color: rgba(255,255,255, 0.1);
                border: 1px solid rgba(250, 250, 250, 0.5);
                color: #ff4b4b;
            }
            /* Adjust top padding to accommodate navbar */
            .block-container {
                padding-top: 3rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    col_title, col1, col2, col3, col_gap, col_utils1, col_utils2 = st.columns([1.5, 1.5, 1.5, 1.5, 2.5, 3, 1.5], vertical_alignment="center")
    
    with col_title:
        st.markdown("#### Gastos")

    with col1:
        with st.popover("Reports", use_container_width=True):
            st.page_link("pages/1_views/1_overview.py", label="Overview", icon=":material/dashboard:")
            st.page_link("pages/1_views/2_trends.py", label="Trends", icon=":material/trending_up:")
            st.page_link("pages/1_views/3_income.py", label="Ingresos", icon=":material/inventory_2:")
            st.page_link("pages/1_views/4_transactions.py", label="Transacciones", icon=":material/inventory_2:")
            st.page_link("pages/1_views/4_config.py", label="Configuración", icon=":material/settings:")
            
    with col2:
        with st.popover("Tools", use_container_width=True):
            st.page_link("pages/2_tools/1_data_explorer.py", label="Explorar Datos", icon=":material/search:")
            st.page_link("pages/2_tools/2_validations.py", label="Validaciones", icon=":material/warning:")
            st.page_link("pages/2_tools/3_data_uploads.py", label="Data Uploads", icon=":material/upload_file:")
            st.page_link("pages/2_tools/4_search.py", label="Search", icon=":material/search:")
            
    with col3:
        with st.popover("Dev", use_container_width=True):
            st.page_link("pages/3_dev/1_staging.py", label="Staging", icon=":material/steppers:")
            st.page_link("pages/3_dev/2_intermediate.py", label="Intermediate", icon=":material/factory:")
            st.page_link("pages/3_dev/3_marts.py", label="Marts", icon=":material/rocket:")
            st.page_link("pages/3_dev/4_exposures.py", label="Exposures", icon=":material/bar_chart_4_bars:")
            st.page_link("pages/3_dev/5_catalog.py", label="Catalog", icon=":material/view_list:")
            st.page_link("pages/3_dev/model_details.py", label="Model Details", icon=":material/info:")
            
    with col_utils1:
        if st.button("Refresh Gsheet Data", icon=":material/refresh:", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
            
    with col_utils2:
        app_version = get_app_version()
        st.caption(f"v{app_version}")
        
    st.divider()
