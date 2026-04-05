#!/usr/bin/env python3
"""
One-time migration script: Cloud SQL (PostgreSQL) → SQLite (local) → GCS

Run this ONCE to bootstrap the SQLite file in your GCS bucket.
After this script succeeds, you can disable the Cloud SQL instance.

Usage:
    cd /path/to/spendee-dashboard
    python scripts/database/seed_sqlite.py

Requirements:
    - .streamlit/secrets.toml must still contain the [gcp_cloud_sql] section
      with valid Cloud SQL credentials.
    - The [gcp_gcs] section must also be present with BUCKET_NAME and DB_PATH.
    - google-cloud-storage, cloud-sql-python-connector, pg8000 must be installed
      (they can be removed from requirements.txt after this script has been run).
"""

import os
import sys
import sqlite3
import pathlib

import pandas as pd
import sqlalchemy
import tomli

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

SECRETS_PATH = _project_root / ".streamlit" / "secrets.toml"
STAGING_TABLE = "stg_transaction"


def load_secrets() -> dict:
    if not SECRETS_PATH.exists():
        raise FileNotFoundError(f"Secrets file not found: {SECRETS_PATH}")
    with open(SECRETS_PATH, "rb") as f:
        return tomli.load(f)


def get_cloud_sql_engine(secrets: dict):
    """Return a SQLAlchemy engine connected to Cloud SQL (PostgreSQL)."""
    from google.cloud.sql.connector import Connector

    cfg = secrets["gcp_cloud_sql"]

    connector = Connector()

    def getconn():
        return connector.connect(
            cfg["INSTANCE_CONNECTION_NAME"],
            "pg8000",
            user=cfg["DB_USER"],
            password=cfg["DB_PASS"],
            db=cfg["DB_NAME"],
        )

    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return engine


def get_sqlite_engine() -> sqlalchemy.Engine:
    """Return a SQLAlchemy engine pointing at the local SQLite file."""
    os.makedirs(os.path.dirname(LOCAL_DB_PATH), exist_ok=True)
    return sqlalchemy.create_engine(
        f"sqlite:///{LOCAL_DB_PATH}",
        connect_args={"check_same_thread": False},
    )


# ---------------------------------------------------------------------------
# Main migration
# ---------------------------------------------------------------------------

def migrate():
    print("=" * 60)
    print("  Spendee: Cloud SQL → SQLite → GCS migration")
    print("=" * 60)

    # 1. Load secrets
    print("\n[1/4] Loading secrets...")
    secrets = load_secrets()
    print(f"      Bucket : {secrets['gcp_gcs']['BUCKET_NAME']}")
    print(f"      DB path: {secrets['gcp_gcs']['DB_PATH']}")

    # 2. Read all rows from Cloud SQL
    print(f"\n[2/4] Connecting to Cloud SQL and reading '{STAGING_TABLE}'...")
    cloud_engine = get_cloud_sql_engine(secrets)
    with cloud_engine.connect() as conn:
        df = pd.read_sql(f"SELECT * FROM {STAGING_TABLE}", conn)
    print(f"      Loaded {len(df):,} rows | columns: {list(df.columns)}")

    # 3. Write to local SQLite
    print(f"\n[3/4] Writing to local SQLite at {LOCAL_DB_PATH}...")
    if os.path.exists(LOCAL_DB_PATH):
        answer = input(f"      ⚠️  {LOCAL_DB_PATH} already exists. Overwrite? [y/N] ").strip().lower()
        if answer != "y":
            print("      Aborted.")
            return

    sqlite_engine = get_sqlite_engine()
    with sqlite_engine.begin() as conn:
        df.to_sql(STAGING_TABLE, conn, if_exists="replace", index=False, chunksize=1000)

    # Verify
    with sqlite_engine.connect() as conn:
        count = conn.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM {STAGING_TABLE}")).scalar()
    print(f"      SQLite table '{STAGING_TABLE}' has {count:,} rows. ✅")

    # 4. Upload to GCS
    print("\n[4/4] Uploading SQLite file to GCS...")
    upload_db()
    print("\n✅  Migration complete! The GCS bucket now contains a seeded SQLite database.")
    print("    You can now disable the Cloud SQL instance and remove its credentials.")


if __name__ == "__main__":
    migrate()
