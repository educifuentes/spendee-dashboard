import streamlit as st
import pandas as pd
from google.cloud.sql.connector import Connector
import sqlalchemy

# Initialize Connector object
connector = Connector()

def getconn():
    conn = connector.connect(
        st.secrets["gcp_cloud_sql"]["INSTANCE_CONNECTION_NAME"],
        "pg8000",
        user=st.secrets["gcp_cloud_sql"]["DB_USER"],
        password=st.secrets["gcp_cloud_sql"]["DB_PASS"],
        db=st.secrets["gcp_cloud_sql"]["DB_NAME"],
    )
    return conn

@st.cache_resource
def get_engine():
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return pool

@st.cache_data(ttl=600)
def stg_cloud_sql__transactions():
    """
    Loads all transactions from the Cloud SQL 'transactions' table into a pandas DataFrame.
    """
    pool = get_engine()
    
    with pool.connect() as db_conn:
        # Use pandas read_sql for convenience
        df = pd.read_sql("SELECT * FROM transactions", db_conn)
    
    return df