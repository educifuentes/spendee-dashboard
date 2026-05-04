import streamlit as st

from helpers.app_version import get_git_version

# ==========================================
# Page Configuration
# ==========================================
st.set_page_config(
    page_title="Spendee Dashboard :material/paid:",
    page_icon=":material/paid:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Section - Reports
overview_page = st.Page("pages/1_views/1_overview.py", title="Overview", icon=":material/dashboard:")
trends_page = st.Page("pages/1_views/2_trends.py", title="Trends", icon=":material/trending_up:")
income_page = st.Page("pages/1_views/3_income.py", title="Ingresos", icon=":material/inventory_2:")
transactions_page = st.Page("pages/1_views/4_transactions.py", title="Transacciones", icon=":material/inventory_2:")


# Section - Tools
explore_page = st.Page("pages/2_tools/1_data_explorer.py", title="Explorar Datos", icon=":material/search:")
validations_page = st.Page("pages/2_tools/2_validations.py", title="Validaciones", icon=":material/warning:")
uploads_page = st.Page("pages/2_tools/3_data_uploads.py", title="Data Uploads", icon=":material/upload_file:")
search_page = st.Page("pages/2_tools/4_search.py", title="Search", icon=":material/search:")

# Section - Dev
staging_page = st.Page("pages/3_dev/1_staging.py", title="Staging", icon=":material/steppers:")
intermediate_page = st.Page("pages/3_dev/2_intermediate.py", title="Intermediate", icon=":material/factory:")
marts_page = st.Page("pages/3_dev/3_marts.py", title="Marts", icon=":material/rocket:")
exposures_page = st.Page("pages/3_dev/4_exposures.py", title="Exposures", icon=":material/bar_chart_4_bars:")
catalog_page = st.Page("pages/3_dev/5_catalog.py", title="Catalog", icon=":material/view_list:")
model_details_page = st.Page("pages/3_dev/model_details.py", title="Model Details", icon=":material/info:")

# current page
pg = st.navigation({
    "Reports": [overview_page, trends_page, income_page],
    "Tools": [explore_page, validations_page, search_page, uploads_page],
    "Dev": [staging_page, intermediate_page, marts_page, exposures_page, catalog_page, model_details_page]
})

# Sidebar - Utilities
with st.sidebar:
    st.divider()
    if st.button("Refresh Gsheet Data", icon=":material/refresh:", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    app_version = get_git_version()
    st.caption(f"App Version: {app_version}")

pg.run()
