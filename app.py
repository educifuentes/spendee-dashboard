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
overview_page = st.Page("pages/reports/1_overview.py", title="Overview", icon=":material/dashboard:")
transactions_page = st.Page("pages/reports/2_transactions.py", title="Transactions", icon=":material/inventory_2:")
budgets_page = st.Page("pages/reports/3_budgets.py", title="Budgets", icon=":material/inventory_2:")
income_page = st.Page("pages/reports/4_income.py", title="Income", icon=":material/inventory_2:")


# Section - Tools
uploads_page = st.Page("pages/tools/1_data_uploads.py", title="Data Uploads", icon=":material/upload_file:")
explore_page = st.Page("pages/tools/2_data_explorer.py", title="Data Explorer", icon=":material/search:")
validations_page = st.Page("pages/tools/3_data_outliers.py", title="Data Outliers", icon=":material/warning:")

# current page
pg = st.navigation({
    "Reports": [overview_page, transactions_page, budgets_page, income_page],
    "Tools": [uploads_page, explore_page, validations_page]
})

# ==========================================
# Authentication
# ==========================================
if not st.user.is_logged_in:
    st.title("Spendee Dashboard")
    st.write("Please log in to access the dashboard.")
    if st.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()
    st.stop()  # Stop execution if not logged in

# Check if user is allowed
if st.user.email not in st.secrets["allowed_emails"]:
    st.title("Access Denied")
    st.error(f"User '{st.user.email}' is not authorized to access this application.")
    if st.button("Log out"):
        st.logout()
    st.stop()  # Stop execution if not authorized

# Show user info and logout in sidebar
with st.sidebar:
    st.divider()
    st.write(f"Logged in as: **{st.user.email}**")
    if st.button("Log out", icon=":material/logout:"):
        st.logout()

pg.run()
