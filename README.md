# Spendee Expense Dashboard

A Streamlit BI dashboard for visualizing personal expenses from a Google Cloud SQL PostgreSQL database.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure database credentials in `.streamlit/secrets.toml`:

```toml
[gcp_cloud_sql]
INSTANCE_CONNECTION_NAME = "project:region:instance"
DB_USER = "postgres"
DB_PASS = "your-password"
DB_NAME = "postgres"
TABLE_NAME = "transactions"
CSV_FILE = "seeds/uploads/fct_transactions.csv"
```

3. Initialize the database (optional - loads data from CSV to Cloud SQL):

```bash
python scripts/load_transactions_cloud_sql.py
```

4. Launch the Streamlit app:

```bash
streamlit run app.py
```

# Deploy

To deploy the application to Google Cloud Run, ensure you have the `gcloud` CLI installed and authenticated, then run the deployment script:

```bash


./scripts/release.sh
```
