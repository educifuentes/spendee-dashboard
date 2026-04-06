import os
import sys
import pathlib

# ---------------------------------------------------------------------------
# Bootstrap: add project root to sys.path so helpers are importable
# ---------------------------------------------------------------------------
_project_root = pathlib.Path(__file__).resolve().parents[1]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from helpers.gcs_handler import upload_db, LOCAL_DB_PATH

def main():
    print(f"Checking for local DB at {LOCAL_DB_PATH}...")
    if not os.path.exists(LOCAL_DB_PATH):
        print(f"❌  LOCAL_DB_PATH not found at {LOCAL_DB_PATH}!")
        return

    print(f"Found local DB (size: {os.path.getsize(LOCAL_DB_PATH):,} bytes).")
    print(f"🚀  Forcing upload to GCS...")
    
    try:
        upload_db()
        print("\n✅  Success! The SQLite database has been uploaded to GCS.")
    except Exception as e:
        print(f"\n❌  Upload failed: {e}")
        # If it's a 404 for the bucket, let's identify it.
        if "404" in str(e):
            print("Note: The 404 might mean the bucket itself does not exist or the object is not found.")

if __name__ == "__main__":
    main()
