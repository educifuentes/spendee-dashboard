"""
SQLite Loader — helpers/sqlite_loader.py

Thin wrapper around sqlalchemy + LOCAL_DB_PATH that follows the
Download-Query-Upload pattern: download the DB from GCS (once per session),
then query it locally, and optionally re-upload after writes.

Public API
----------
load_from_sqlite(table, *, columns, where, limit)  -> pd.DataFrame
get_latest_transaction_date(table)                  -> pd.Timestamp | None
insert_into_sqlite(df, table, *, upload_to_gcs)    -> int   (rows inserted)
"""

from __future__ import annotations

import os
import pandas as pd
import sqlalchemy

from helpers.gcs_handler import LOCAL_DB_PATH, download_db


# ---------------------------------------------------------------------------
# Internal: engine (singleton per process)
# ---------------------------------------------------------------------------

_engine: sqlalchemy.Engine | None = None

# Fallback schema for when the database is empty or missing
_SCHEMA_FALLBACK = [
    'date', 'wallet', 'type', 'category', 'amount', 'currency', 'note', 'labels',
    'day', 'week', 'month', 'year', 'amount_universal_clp', 'budget', 'record_hash', 'id'
]


def _get_engine() -> sqlalchemy.Engine | None:
    global _engine
    if _engine is None:
        if not os.path.exists(LOCAL_DB_PATH):
            print(f"[sqlite_loader] ⚠️  Warning: DB not found at {LOCAL_DB_PATH}.")
            return None
            
        _engine = sqlalchemy.create_engine(
            f"sqlite:///{LOCAL_DB_PATH}",
            connect_args={"check_same_thread": False},
        )
    return _engine


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_from_sqlite(
    table: str,
    *,
    columns: list[str] | None = None,
    where: str | None = None,
    limit: int | None = None,
    ensure_downloaded: bool = True,
) -> pd.DataFrame:
    """
    Load rows from a SQLite table into a DataFrame.
    """
    if ensure_downloaded:
        download_db()  # Returns bool, but we check file existence via _get_engine

    engine = _get_engine()
    if engine is None:
        # DB doesn't exist locally — return empty DF with schema to avoid crashes
        return pd.DataFrame(columns=_SCHEMA_FALLBACK)

    col_clause = ", ".join(columns) if columns else "*"
    sql = f"SELECT {col_clause} FROM {table}"
    if where:
        sql += f" WHERE {where}"
    if limit is not None:
        sql += f" LIMIT {limit}"

    try:
        with engine.connect() as conn:
            df = pd.read_sql(sqlalchemy.text(sql), conn)
    except Exception as e:
        print(f"[sqlite_loader] ❌  Failed to query table '{table}': {e}")
        return pd.DataFrame(columns=_SCHEMA_FALLBACK)

    return df


def get_latest_transaction_date(
    table: str = "stg_transaction",
    date_col: str = "date",
) -> "pd.Timestamp | None":
    """
    Return the most recent date stored in *table*, or None if the table is empty.
    """
    download_db()
    sql = f"SELECT MAX({date_col}) FROM {table}"
    with _get_engine().connect() as conn:
        result = conn.execute(sqlalchemy.text(sql)).scalar()
    if result is None:
        return None
    return pd.to_datetime(result)


def insert_into_sqlite(
    df: "pd.DataFrame",
    table: str = "stg_transaction",
    *,
    hash_col: str = "record_hash",
    upload_to_gcs: bool = True,
) -> int:
    """
    Insert only rows whose *hash_col* is not already in *table*.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame produced by ``process_raw_spendee_csv()``.
    table : str
        Target SQLite table (default ``"stg_transaction"``).
    hash_col : str
        Column used for deduplication (default ``"record_hash"``).
    upload_to_gcs : bool
        If True (default), re-upload the SQLite file to GCS after inserting.

    Returns
    -------
    int
        Number of rows actually inserted.
    """
    from helpers.gcs_handler import upload_db  # local import to avoid circular

    download_db()
    engine = _get_engine()

    # Fetch existing hashes for dedup
    with engine.connect() as conn:
        try:
            existing = set(
                pd.read_sql(
                    sqlalchemy.text(f"SELECT {hash_col} FROM {table}"), conn
                )[hash_col].tolist()
            )
        except Exception:
            existing = set()  # table might not exist yet

    new_rows = df[~df[hash_col].isin(existing)].copy() if hash_col in df.columns else df.copy()

    if new_rows.empty:
        return 0

    # Keep only columns that exist in the table (for safety)
    with engine.connect() as conn:
        try:
            db_cols = pd.read_sql(
                sqlalchemy.text(f"SELECT * FROM {table} LIMIT 1"), conn
            ).columns.tolist()
            insert_cols = [c for c in new_rows.columns if c in db_cols]
            new_rows = new_rows[insert_cols]
        except Exception:
            pass  # table empty / new — insert all columns

    with engine.begin() as conn:
        new_rows.to_sql(table, conn, if_exists="append", index=False, chunksize=500)

    if upload_to_gcs:
        upload_db()

    return len(new_rows)
