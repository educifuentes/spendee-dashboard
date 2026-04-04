import streamlit as st

from helpers.utilities.model_catalog import build_global_model_registry
from helpers.utilities.find_model import find_model
from helpers.ui_components.render_model import render_model_ui
from helpers.ui_components.icons import render_icon

st.title("Exposures")

df_catalog = build_global_model_registry("models")
# In catalog generation, stage would be either 'exposures' or 'exposures' depending on naming
# But typically the folder name for standard structure is "exposures" or similar.
# Assuming here it is 'exposures':
df_stage = df_catalog[df_catalog["stage"] == "exposures"]

if not df_stage.empty:
    schemas = sorted(df_stage["schema"].unique().tolist())
    
    tabs = st.tabs([schema.replace("_", " ").title() for schema in schemas])
    
    for i, schema in enumerate(schemas):
        with tabs[i]:
            st.header(schema.replace("_", " ").title())
            
            df_schema = df_stage[df_stage["schema"] == schema]
            for _, row in df_schema.iterrows():
                model_name = row["model"]
                df = find_model(model_name)
                
                if df is not None:
                    render_model_ui(df, table_name=model_name)
else:
    st.info("No BI tables (exposures) found.")
