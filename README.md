# Spendee Expense Dashboard

A Streamlit BI dashboard for visualizing personal expenses, using a SQLite database synced to a Google Cloud Storage (GCS) bucket.

# Deploy

To deploy the application to Google Cloud Run, ensure you have the `gcloud` CLI installed and authenticated, then run the deployment script:

```bash
./scripts/release.sh
```

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure storage credentials in `.streamlit/secrets.toml`:

```toml
[gcp_gcs]
BUCKET_NAME = "your-bucket-name"
DB_PATH = "expenses.sqlite"
```

3. Initialize the database (optional - loads data from CSV to a local SQLite file, then uploads to GCS):

```bash
python scripts/database/seed_sqlite.py
```

_(Note: This replaces the legacy `scripts/database/load_all_stg_transactions.py` which was used for Cloud SQL)._

4. Launch the Streamlit app:

```bash
streamlit run app.py
```
