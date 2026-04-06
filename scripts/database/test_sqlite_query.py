#!/usr/bin/env python3
"""
Quick sanity-check: query the local SQLite database and print the first 20 rows.

Usage:
    cd /path/to/spendee-dashboard
    python scripts/database/test_sqlite_query.py
"""

import os
import sys
import pathlib

import pandas as pd
import sqlalchemy

# ---------------------------------------------------------------------------
# Bootstrap: add project root to sys.path so helpers are importable
# ---------------------------------------------------------------------------
_script_dir   = pathlib.Path(__file__).resolve().parent
_project_root = _script_dir.parents[1]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from helpers.gcs_handler import LOCAL_DB_PATH  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TABLE = "stg_transaction"
LIMIT = 20


def main():
    print("=" * 60)
    print("  SQLite DB sanity check")
    print("=" * 60)
    print(f"\n  DB path : {LOCAL_DB_PATH}")
    print(f"  Table   : {TABLE}")
    print(f"  Limit   : {LIMIT}\n")

    # Check file exists
    if not os.path.exists(LOCAL_DB_PATH):
        print(f"❌  Database file not found at: {LOCAL_DB_PATH}")
        sys.exit(1)

    engine = sqlalchemy.create_engine(
        f"sqlite:///{LOCAL_DB_PATH}",
        connect_args={"check_same_thread": False},
    )

    with engine.connect() as conn:
        # Total row count
        total = conn.execute(
            sqlalchemy.text(f"SELECT COUNT(*) FROM {TABLE}")
        ).scalar()
        print(f"  Total rows in '{TABLE}': {total:,}")

        if total == 0:
            print("\n⚠️  Table exists but has NO rows.")
            sys.exit(1)

        # Sample rows
        df = pd.read_sql(
            sqlalchemy.text(f"SELECT * FROM {TABLE} LIMIT {LIMIT}"),
            conn,
        )

    print(f"\n✅  First {LIMIT} rows:\n")
    print(df.to_string(index=False))
    print(f"\n  Columns: {list(df.columns)}")


if __name__ == "__main__":
    main()
