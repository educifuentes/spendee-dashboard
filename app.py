import streamlit as st


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
income_page = st.Page("pages/1_views/3_income.py", title="Income", icon=":material/inventory_2:")
transactions_page = st.Page("pages/1_views/4_transactions.py", title="Transactions", icon=":material/inventory_2:")


# Section - Tools
explore_page = st.Page("pages/2_tools/1_data_explorer.py", title="Data Explorer", icon=":material/search:")
validations_page = st.Page("pages/2_tools/2_validations.py", title="Validations", icon=":material/warning:")
uploads_page = st.Page("pages/2_tools/3_data_uploads.py", title="Data Uploads", icon=":material/upload_file:")
search_page = st.Page("pages/2_tools/4_search.py", title="Search", icon=":material/search:")

# Section - Dev
staging_page = st.Page("pages/3_data_build/1_staging.py", title="Staging", icon=":material/database:")
marts_page = st.Page("pages/3_data_build/2_marts.py", title="Marts", icon=":material/database:")
bi_tables_page = st.Page("pages/3_data_build/3_bi_tables.py", title="BI Tables", icon=":material/database:")
config_page = st.Page("pages/3_data_build/4_config.py", title="Configuration", icon=":material/settings:")

# current page
pg = st.navigation({
    "Reports": [overview_page, trends_page, income_page, transactions_page],
    "Tools": [explore_page, validations_page, search_page, uploads_page],
    "Dev": [staging_page, marts_page, bi_tables_page, config_page]
})

pg.run()
