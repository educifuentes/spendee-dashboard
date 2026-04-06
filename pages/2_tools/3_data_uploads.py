"""
Upload Spendee CSV and sync to the GCS-hosted SQLite database.
"""
import streamlit as st

from helpers.ui_components.icons import ICONS
from helpers.upload_handler import render_upload_ui

st.title(f"{ICONS['upload']} Upload Data")

render_upload_ui()
