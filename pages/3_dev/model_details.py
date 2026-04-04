import streamlit as st

from helpers.ui_components.model_details_ui import render_model_details
from helpers.utilities.model_catalog import build_global_model_registry

st.title("Model Details")

df_catalog = build_global_model_registry("models")
model_names = df_catalog["model"].tolist() if not df_catalog.empty else []

# Retrieve query params from URL or session state
default_model_name = st.query_params.get("model") or st.session_state.get("selected_model")

# Determine default index for the selectbox
default_index = 0
if default_model_name in model_names:
    default_index = model_names.index(default_model_name)

# Selectbox to pick a model
model_name = st.selectbox("Select Model", options=model_names, index=default_index)

# Render the details for the selected model
if model_name:
    render_model_details(model_name)
else:
    st.info("No models found. Please create some models first.")
