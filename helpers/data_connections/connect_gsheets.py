import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd


@st.cache_data
def load_data_gsheets(worksheet: str) -> pd.DataFrame:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    df = conn.read(worksheet=worksheet)
    return df

