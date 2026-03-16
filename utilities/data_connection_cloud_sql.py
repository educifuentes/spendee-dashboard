import streamlit as st
import pandas as pd
from google.cloud.sql.connector import Connector
import sqlalchemy

@st.cache_resource
def get_engine():
    # Initialize Connector inside the cached function
    connector = Connector()
    
    def getconn():
        return connector.connect(
            st.secrets["gcp_cloud_sql"]["INSTANCE_CONNECTION_NAME"],
            "pg8000",
            user=st.secrets["gcp_cloud_sql"]["DB_USER"],
            password=st.secrets["gcp_cloud_sql"]["DB_PASS"],
            db=st.secrets["gcp_cloud_sql"]["DB_NAME"],
        )
        
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return pool

@st.cache_data(ttl=600)
def load_transactions():
    """
    Loads all transactions from the Cloud SQL 'transactions' table into a pandas DataFrame.
    """
    pool = get_engine()
    
    with pool.connect() as db_conn:
        # Use pandas read_sql for convenience
        df = pd.read_sql("SELECT * FROM transactions", db_conn)
    
    return df

@st.cache_data(ttl=600)
def load_stg_transactions():
    """
    Loads all transactions from the Cloud SQL 'stg_transaction' staging table into a pandas DataFrame.
    This table contains the raw data loaded via scripts before any transformations.
    """
    pool = get_engine()
    
    with pool.connect() as db_conn:
        df = pd.read_sql("SELECT * FROM stg_transaction", db_conn)
    
    return df

def update_transaction(transaction_id, changes):
    """
    Update a transaction in Cloud SQL.
    changes: dict of column name -> new value
    """
    pool = get_engine()
    with pool.connect() as conn:
        # Construct SET clause dynamically
        # Be careful with SQL injection; use parameters
        set_clauses = []
        params = {"id": transaction_id}
        
        for i, (col, val) in enumerate(changes.items()):
            param_name = f"val_{i}"
            set_clauses.append(f"{col} = :{param_name}")
            params[param_name] = val
            
        if not set_clauses:
            return

        stmt = sqlalchemy.text(f"UPDATE transactions SET {', '.join(set_clauses)} WHERE id = :id")
        conn.execute(stmt, params)
        conn.commit()

def delete_transaction(transaction_id):
    """
    Delete a transaction from Cloud SQL.
    """
    pool = get_engine()
    with pool.connect() as conn:
        stmt = sqlalchemy.text("DELETE FROM transactions WHERE id = :id")
        conn.execute(stmt, {"id": transaction_id})
        conn.commit()
