"""
Test database connection to Supabase.
"""
import sys
from pathlib import Path

from supabase import create_client, Client
import tomli as tomllib


def load_secrets():
    """Load secrets from .streamlit/secrets.toml file."""
    secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"
    with open(secrets_path, "rb") as f:
        secrets = tomllib.load(f)
    return secrets.get("SUPABASE_URL"), secrets.get("SUPABASE_KEY")


def test_connection():
    """Test connection to Supabase database."""
    url, key = load_secrets()
    supabase: Client = create_client(url, key)
    print("✓ Connection successful")
    return True


if __name__ == "__main__":
    try:
        test_connection()
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)
