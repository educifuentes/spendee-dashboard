"""
SQLite Loader — helpers/sqlite_loader.py

Thin wrapper around sqlalchemy + LOCAL_DB_PATH that follows the
Download-Query-Upload pattern: download the DB from GCS (once per session),
then query it locally.

Public API
----------
load_from_sqlite(table, *, columns=None, where=None, limit=None) -> pd.DataFrame
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


def _get_engine() -> sqlalchemy.Engine:
    global _engine
    if _engine is None:
        if not os.path.exists(LOCAL_DB_PATH):
            raise FileNotFoundError(
                f"[sqlite_loader] DB not found at {LOCAL_DB_PATH}. "
                "Call download_db() first or run the seed script."
            )
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

    Parameters
    ----------
    table : str
        Table name to query (e.g. ``"stg_transaction"``).
    columns : list[str] | None
        Columns to SELECT. Defaults to ``*``.
    where : str | None
        Optional SQL WHERE clause (without the ``WHERE`` keyword).
        Example: ``"type = 'Expense'"``
    limit : int | None
        Optional LIMIT clause.
    ensure_downloaded : bool
        If True (default), call ``download_db()`` to pull the DB from GCS
        when it is not already present locally.

    Returns
    -------
    pd.DataFrame
    """
    if ensure_downloaded:
        download_db()  # no-op if already present

    col_clause = ", ".join(columns) if columns else "*"
    sql = f"SELECT {col_clause} FROM {table}"
    if where:
        sql += f" WHERE {where}"
    if limit is not None:
        sql += f" LIMIT {limit}"

    with _get_engine().connect() as conn:
        df = pd.read_sql(sqlalchemy.text(sql), conn)

    return df
