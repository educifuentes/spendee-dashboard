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
search_page = st.Page("pages/tools/4_search.py", title="Search", icon=":material/search:")

# current page
pg = st.navigation({
    "Reports": [overview_page, transactions_page, budgets_page, income_page],
    "Tools": [uploads_page, explore_page, validations_page, search_page]
})

# ==========================================
# Authentication
# ==========================================
# if not st.user.get("is_logged_in"):
#     st.title("Spendee Dashboard")
#     # DEBUG
#     st.write(st.secrets)
#     try:
#         st.write("Config Options:")
#         st.write({
#             "server.enableXsrfProtection": st.get_option("server.enableXsrfProtection"),
#             "server.enableCORS": st.get_option("server.enableCORS"),
#             "server.headless": st.get_option("server.headless"),
#         })
#     except Exception as e:
#         st.write(f"Could not read config: {e}")
#     st.write(st.user)

#     st.write("Please log in to access the dashboard.")
#     if st.button("Log in with Google", type="primary", icon=":material/login:"):
#         st.login()
#     st.stop()  # Stop execution if not logged in

# Check if user is allowed
# user_email = st.user.get("email")
# allowed_emails = st.secrets.get("allowed_emails", [])
# if isinstance(allowed_emails, str):
#     allowed_emails = [email.strip() for email in allowed_emails.split(",")]
# if user_email not in allowed_emails:
#     st.title("Access Denied")
#     st.error(f"User '{user_email}' is not authorized to access this application.")
#     if st.button("Log out"):
#         st.logout()
#     st.stop()  # Stop execution if not authorized

# # Show user info and logout in sidebar
# with st.sidebar:
#     st.divider()
#     st.write(f"Logged in as: **{user_email}**")
#     if st.button("Log out", icon=":material/logout:"):
#         st.logout()

pg.run()
