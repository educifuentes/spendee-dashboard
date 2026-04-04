import streamlit as st
from helpers.utilities.find_model import find_model
from helpers.ui_components.render_model import render_model_ui

def render_model_details(model_name: str):
    if model_name:
        st.header(f"Model: {model_name}")
        
        df = find_model(model_name)
        
        if df is not None:
            # 5. Render exact visualizations automatically
            
            st.subheader("Dataframe")
            render_model_ui(df, table_name=model_name)
    else:
        st.warning("No Model Selected.")
