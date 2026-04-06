#!/usr/bin/env python3
"""
Seed script: CSV → SQLite (local) → GCS

Reads the pre-processed fct_transactions.csv from seeds/uploads/,
writes it into a fresh SQLite file, then uploads it to GCS.

Usage:
    cd /path/to/spendee-dashboard
    python scripts/database/seed_sqlite.py
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

from helpers.gcs_handler import upload_db, LOCAL_DB_PATH  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

STAGING_TABLE = "stg_transaction"
CSV_SOURCE    = _project_root / "seeds" / "uploads" / "fct_transactions.csv"


def get_sqlite_engine() -> sqlalchemy.Engine:
    os.makedirs(os.path.dirname(LOCAL_DB_PATH), exist_ok=True)
    return sqlalchemy.create_engine(
        f"sqlite:///{LOCAL_DB_PATH}",
        connect_args={"check_same_thread": False},
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def migrate():
    print("=" * 60)
    print("  Spendee: CSV → SQLite → GCS seed")
    print("=" * 60)

    # 1. Read CSV
    print(f"\n[1/3] Reading {CSV_SOURCE.relative_to(_project_root)} ...")
    if not CSV_SOURCE.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_SOURCE}")

    df = pd.read_csv(CSV_SOURCE)
    print(f"      Loaded {len(df):,} rows | columns: {list(df.columns)}")

    # Normalise date column
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], utc=True).dt.tz_localize(None)

    # 2. Write to SQLite
    print(f"\n[2/3] Writing to SQLite at {LOCAL_DB_PATH} ...")
    if os.path.exists(LOCAL_DB_PATH):
        print(f"      ⚠️  Existing database found. Deleting for a fresh start to ensure all tables are overwritten.")
        os.remove(LOCAL_DB_PATH)

    engine = get_sqlite_engine()
    with engine.begin() as conn:
        df.to_sql(STAGING_TABLE, conn, if_exists="replace", index=False, chunksize=1000)

    with engine.connect() as conn:
        count = conn.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM {STAGING_TABLE}")).scalar()
    print(f"      SQLite table '{STAGING_TABLE}' has {count:,} rows. ✅")

    # 3. Upload to GCS
    print("\n[3/3] Uploading SQLite file to GCS ...")
    upload_db()
    print("\n✅  Done! The GCS bucket now contains a seeded SQLite database.")
    print("    You can safely disable Cloud SQL and remove its credentials from secrets.toml.")


if __name__ == "__main__":
    migrate()
