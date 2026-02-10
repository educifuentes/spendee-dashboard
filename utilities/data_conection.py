import os

import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_supabase() -> Client:
    """
    Initialize and return Supabase client.
    Cached with st.cache_resource to reuse the client across sessions.
    
    On Heroku (production), reads credentials from environment variables.
    On local development, reads from Streamlit secrets.
    """
    # Check if running on Heroku (production)
    is_production = os.environ.get("DYNO") is not None
    
    if is_production:
        # Heroku: read from environment variables
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
    else:
        # Local: read from Streamlit secrets
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    
    if not url or not key:
        raise ValueError(
            "Supabase credentials not found. "
            "Set SUPABASE_URL and SUPABASE_KEY in environment variables (production) "
            "or in .streamlit/secrets.toml (local development)."
        )
    
    return create_client(url, key)
