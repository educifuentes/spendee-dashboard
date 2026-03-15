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

This script will:

1. Upload secrets to GCP Secret Manager (using `scripts/upload_secrets.sh`).
2. Grant necessary IAM permissions.
3. Build the Docker image using Cloud Build.
4. Deploy to Cloud Run.

## Reload Database

To completely reset the database with the full transaction history, run these two scripts in order:

1. **Clean Data**: Exports the latest transactions from the models to a CSV file.

   ```bash
   python scripts/clean_data_transactions_to_csv.py
   ```

2. **Reload Database**: Deletes all existing rows in the database and reloads them from the CSV.
   ```bash
   python scripts/load_transactions_cloud_sql.py
   ```

## Features

- **KPI Panel**: Current month expenses with percentage change vs last month
- **Interactive Filters**: Date range, granularity, category, and label filters
- **Visualizations**: Expenses by category, by month, and top transactions
