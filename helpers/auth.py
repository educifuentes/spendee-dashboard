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