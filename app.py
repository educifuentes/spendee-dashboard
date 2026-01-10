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
overview_page = st.Page("reports/1_overview.py", title="Overview", icon=":material/dashboard:")
transactions_page = st.Page("reports/2_transactions.py", title="Transactions", icon=":material/inventory_2:")
budgets_page = st.Page("reports/3_budgets.py", title="Budgets", icon=":material/inventory_2:")


# Section - Tools
uploads_page = st.Page("tools/1_data_uploads.py", title="Data Uploads", icon=":material/upload_file:")
explore_page = st.Page("tools/2_data_explorer.py", title="Data Explorer", icon=":material/search:")
validations_page = st.Page("tools/3_data_outliers.py", title="Data Outliers", icon=":material/warning:")

# current page
pg = st.navigation({
    "Reports": [overview_page, transactions_page, budgets_page],
    "Tools": [uploads_page, explore_page, validations_page]
})

pg.run()
    