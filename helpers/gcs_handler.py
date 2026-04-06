"""
GCS Handler — Download-Query-Upload pattern for SQLite persistence.

Uses the official google-cloud-storage SDK which authenticates via
Application Default Credentials (ADC). Run `gcloud auth application-default login`
locally, or attach a service account to the Cloud Run deployment.

Secrets layout expected in .streamlit/secrets.toml:

    [gcp_gcs]
    BUCKET_NAME = "your-bucket-name"
    DB_PATH     = "expenses.sqlite"   # object path inside the bucket
"""

import os

LOCAL_DB_PATH = "/tmp/expenses.sqlite"

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_gcs_config():
    """
    Read GCS config from st.secrets (Streamlit context) or secrets.toml (scripts).
    Returns (bucket_name, db_path).
    """
    try:
        import streamlit as st
        bucket  = st.secrets["gcp_gcs"]["BUCKET_NAME"]
        db_path = st.secrets["gcp_gcs"]["DB_PATH"]
    except Exception:
        import tomli, pathlib
        secrets_file = pathlib.Path(__file__).parents[1] / ".streamlit" / "secrets.toml"
        with open(secrets_file, "rb") as f:
            secrets = tomli.load(f)
        bucket  = secrets["gcp_gcs"]["BUCKET_NAME"]
        db_path = secrets["gcp_gcs"]["DB_PATH"]

    return bucket, db_path


def _get_gcs_client():
    """Return an authenticated google.cloud.storage.Client using ADC."""
    from google.cloud import storage
    return storage.Client()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def download_db(force: bool = False) -> bool:
    """
    Download expenses.sqlite from GCS to LOCAL_DB_PATH.

    Parameters
    ----------
    force : bool
        If True, always re-download even if the local file already exists.

    Returns
    -------
    bool
        True if the file exists locally after this call, False otherwise.
    """
    if not force and os.path.exists(LOCAL_DB_PATH):
        return True  # already present, nothing to do

    bucket_name, db_path = _get_gcs_config()
    print(f"[gcs_handler] Downloading gs://{bucket_name}/{db_path} → {LOCAL_DB_PATH}")

    try:
        client = _get_gcs_client()
        bucket = client.bucket(bucket_name)
        blob   = bucket.blob(db_path)

        if not blob.exists():
            print(f"[gcs_handler] ⚠️  Warning: SQLite file not found in GCS.")
            print(f"               Bucket: {bucket_name} | Path: {db_path}")
            print(f"               The app will start with a brand new (empty) database.")
            return False

        os.makedirs(os.path.dirname(LOCAL_DB_PATH), exist_ok=True)
        blob.download_to_filename(LOCAL_DB_PATH)
        print("[gcs_handler] Download complete.")
        return True

    except Exception as e:
        print(f"[gcs_handler] ❌  Error downloading database: {e}")
        if os.path.exists(LOCAL_DB_PATH):
            print("[gcs_handler] Using existing local file since download failed.")
            return True
        return False


def upload_db() -> None:
    """
    Upload the local expenses.sqlite back to GCS, overwriting the remote copy.
    Call this immediately after any INSERT / UPDATE / DELETE.
    """
    if not os.path.exists(LOCAL_DB_PATH):
        raise FileNotFoundError(f"[gcs_handler] Local DB not found at {LOCAL_DB_PATH}")

    bucket_name, db_path = _get_gcs_config()
    print(f"[gcs_handler] Uploading {LOCAL_DB_PATH} → gs://{bucket_name}/{db_path}")

    try:
        client = _get_gcs_client()
        bucket = client.bucket(bucket_name)
        blob   = bucket.blob(db_path)
        blob.upload_from_filename(LOCAL_DB_PATH, content_type="application/octet-stream")
        print("[gcs_handler] Upload complete.")

    except Exception as e:
        print(f"[gcs_handler] ❌  Error uploading database: {e}")
        raise e
