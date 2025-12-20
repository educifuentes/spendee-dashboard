# Spendee Expense Dashboard

A Streamlit BI dashboard for visualizing personal expenses from a Supabase PostgreSQL database.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database credentials in `.streamlit/secrets.toml`:
```toml
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
```

3. Launch the Streamlit app:
```bash
streamlit run app.py
```

## Features

- **KPI Panel**: Current month expenses with percentage change vs last month
- **Interactive Filters**: Date range, granularity, category, and label filters
- **Visualizations**: Expenses by category, by month, and top transactions
