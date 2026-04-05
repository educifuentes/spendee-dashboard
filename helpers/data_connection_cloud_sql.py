"""
Database connection layer — SQLite backend (GCS-hosted).

The SQLite file lives at /tmp/expenses.sqlite and is downloaded from GCS on
first access. After any write operation (INSERT / UPDATE / DELETE) the file
is immediately uploaded back so the remote copy stays in sync.

All public function signatures are identical to the previous Cloud SQL version
so that no other code needs to change.
"""

import os
import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import text

from helpers.gcs_handler import download_db, upload_db

LOCAL_DB_PATH = "/tmp/expenses.sqlite"
STAGING_TABLE = "stg_transaction"


# ---------------------------------------------------------------------------
# Engine — cached for the lifetime of the Streamlit session
# ---------------------------------------------------------------------------

@st.cache_resource
def get_engine():
    """
    Return a SQLAlchemy engine pointing at the local SQLite file.
    Downloads the file from GCS first if it's not already present.
    """
    download_db()                               # no-op if file already exists
    engine = sqlalchemy.create_engine(
        f"sqlite:///{LOCAL_DB_PATH}",
        connect_args={"check_same_thread": False},
    )
    return engine


# ---------------------------------------------------------------------------
# Read helpers
# ---------------------------------------------------------------------------

@st.cache_data(ttl=600)
def load_stg_transactions() -> pd.DataFrame:
    """
    Load all rows from the staging table into a DataFrame.
    (Previously pointed at Cloud SQL stg_transaction table.)
    """
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(f"SELECT * FROM {STAGING_TABLE}", conn)
    return df


@st.cache_data(ttl=600)
def load_transactions() -> pd.DataFrame:
    """
    Alias for load_stg_transactions() — kept for backwards compatibility.
    """
    return load_stg_transactions()


def get_latest_transaction_date(engine=None):
    """
    Return the most recent date in the staging table, or None if empty.
    """
    if engine is None:
        engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT MAX(date) AS max_date FROM {STAGING_TABLE}"))
            row = result.fetchone()
            max_date = row[0] if row else None
            if max_date is not None and pd.notnull(max_date):
                return pd.to_datetime(max_date)
    except Exception as e:
        print(f"[data_connection] Error fetching latest date: {e}")
    return None


# ---------------------------------------------------------------------------
# Write helpers  (each one triggers an upload_db() immediately after)
# ---------------------------------------------------------------------------

def insert_new_transactions(df: pd.DataFrame, engine=None) -> int:
    """
    Append new rows to the staging table and sync to GCS.
    Returns the number of rows inserted.
    """
    if df.empty:
        return 0
    if engine is None:
        engine = get_engine()

    with engine.begin() as conn:
        df.to_sql(STAGING_TABLE, conn, if_exists="append", index=False, chunksize=1000)

    # Persist to GCS immediately
    upload_db()

    # Bust the cache so the next read reflects the new rows
    st.cache_data.clear()

    return len(df)


def update_transaction(transaction_id, changes: dict) -> None:
    """
    Update a single transaction row and sync the updated DB to GCS.
    changes: dict of {column_name: new_value}
    """
    if not changes:
        return

    engine = get_engine()
    set_clauses = []
    params = {"id": transaction_id}

    for i, (col, val) in enumerate(changes.items()):
        param_name = f"val_{i}"
        set_clauses.append(f"{col} = :{param_name}")
        params[param_name] = val

    stmt = text(f"UPDATE {STAGING_TABLE} SET {', '.join(set_clauses)} WHERE id = :id")

    with engine.begin() as conn:
        conn.execute(stmt, params)

    upload_db()
    st.cache_data.clear()


def delete_transaction(transaction_id) -> None:
    """
    Delete a transaction row and sync the updated DB to GCS.
    """
    engine = get_engine()
    stmt = text(f"DELETE FROM {STAGING_TABLE} WHERE id = :id")

    with engine.begin() as conn:
        conn.execute(stmt, {"id": transaction_id})

    upload_db()
    st.cache_data.clear()
