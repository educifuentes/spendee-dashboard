import streamlit as st
from streamlit_gsheets import GSheetsConnection

TTL_VALUE = "5m" # 5 minutes

@st.cache_data
def load_gsheets_worksheet(worksheet_name: str):
    """Load a specific worksheet from Google Sheets."""
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=TTL_VALUE)
    df = conn.read(worksheet=worksheet_name)
    df = add_row_number(df)
    return df
