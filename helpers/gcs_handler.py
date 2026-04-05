"""
GCS Handler — Download-Query-Upload pattern for SQLite persistence.

Uses the GCS JSON REST API with an API key (no service-account JSON needed).
The key must have the "Cloud Storage API" enabled in GCP and the target
bucket must be accessible (Storage Object Viewer / Creator at minimum).

Secrets layout expected in .streamlit/secrets.toml:

    [gcp_gcs]
    BUCKET_NAME = "your-bucket-name"
    DB_PATH     = "expenses.sqlite"   # object path inside the bucket

    [gcp_cloud_sql]
    API_KEY_BUCKET = "AIzaSy..."      # re-used from existing section
"""

import os
import requests as _requests

LOCAL_DB_PATH = "/tmp/expenses.sqlite"

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_gcs_config():
    """
    Read GCS config from st.secrets.
    Falls back to reading .streamlit/secrets.toml via tomli when running
    outside of a Streamlit context (e.g., standalone migration scripts).
    """
    try:
        import streamlit as st
        bucket  = st.secrets["gcp_gcs"]["BUCKET_NAME"]
        db_path = st.secrets["gcp_gcs"]["DB_PATH"]
        api_key = st.secrets["gcp_cloud_sql"]["API_KEY_BUCKET"]
    except Exception:
        # Fallback for scripts run outside Streamlit
        import tomli, pathlib
        secrets_file = pathlib.Path(__file__).parents[1] / ".streamlit" / "secrets.toml"
        with open(secrets_file, "rb") as f:
            secrets = tomli.load(f)
        bucket  = secrets["gcp_gcs"]["BUCKET_NAME"]
        db_path = secrets["gcp_gcs"]["DB_PATH"]
        api_key = secrets["gcp_cloud_sql"]["API_KEY_BUCKET"]

    return bucket, db_path, api_key


def _gcs_object_url(bucket: str, db_path: str) -> str:
    """Return the GCS JSON API object URL (URL-encoded object name)."""
    encoded = _requests.utils.quote(db_path, safe="")
    return f"https://storage.googleapis.com/storage/v1/b/{bucket}/o/{encoded}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def download_db(force: bool = False) -> None:
    """
    Download expenses.sqlite from GCS to LOCAL_DB_PATH.

    Parameters
    ----------
    force : bool
        If True, always re-download even if the local file already exists.
    """
    if not force and os.path.exists(LOCAL_DB_PATH):
        return  # already present, nothing to do

    bucket, db_path, api_key = _get_gcs_config()
    url = _gcs_object_url(bucket, db_path)

    print(f"[gcs_handler] Downloading gs://{bucket}/{db_path} → {LOCAL_DB_PATH}")
    resp = _requests.get(url, params={"alt": "media", "key": api_key}, stream=True)
    resp.raise_for_status()

    os.makedirs(os.path.dirname(LOCAL_DB_PATH), exist_ok=True)
    with open(LOCAL_DB_PATH, "wb") as fh:
        for chunk in resp.iter_content(chunk_size=8192):
            fh.write(chunk)
    print("[gcs_handler] Download complete.")


def upload_db() -> None:
    """
    Upload the local expenses.sqlite back to GCS, overwriting the remote copy.
    Call this immediately after any INSERT / UPDATE / DELETE.
    """
    if not os.path.exists(LOCAL_DB_PATH):
        raise FileNotFoundError(f"[gcs_handler] Local DB not found at {LOCAL_DB_PATH}")

    bucket, db_path, api_key = _get_gcs_config()
    upload_url = (
        f"https://storage.googleapis.com/upload/storage/v1/b/{bucket}/o"
        f"?uploadType=media&name={_requests.utils.quote(db_path, safe='')}&key={api_key}"
    )

    print(f"[gcs_handler] Uploading {LOCAL_DB_PATH} → gs://{bucket}/{db_path}")
    with open(LOCAL_DB_PATH, "rb") as fh:
        data = fh.read()

    resp = _requests.post(
        upload_url,
        data=data,
        headers={"Content-Type": "application/octet-stream"},
    )
    resp.raise_for_status()
    print("[gcs_handler] Upload complete.")
