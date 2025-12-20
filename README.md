# Spendee Expense Dashboard

A Streamlit BI dashboard for visualizing personal expenses exported from the Spendee app.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the data cleaning script to generate cleaned data:
```bash
python utils/clean.py
```

3. Launch the Streamlit app:
```bash
streamlit run app.py
```

## Project Structure

```
project_root/
│
├─ app.py                    # Single-page Streamlit app
│
├─ data/
│   ├─ raw/                  # Raw input CSV files
│   └─ clean/                # Cleaned and processed outputs
│       └─ expenses_main-clp_clean.csv
│
├─ utils/
│   ├─ clean.py              # Data cleaning functions
│   ├─ transforms.py         # Aggregations and data preparation
│   └─ charts.py             # Altair chart definitions
│
├─ constants/
│   └─ budgets.json          # Budget category mapping
│
└─ .streamlit/
└─ config.toml           # Dark theme configuration
```

## Features

- **KPI Panel**: Current month expenses with percentage change vs last month
- **Interactive Filters**: Date range, granularity, category, and label filters
- **Visualizations**:
  - Expenses by Category (for selected period)
  - Expenses by Month (current year)
  - Top 10 Transactions (current month)

## Data Cleaning

The `utils/clean.py` module:
- Renames columns to lowercase
- Maps "Category name" to "category"
- Converts amounts to absolute values
- Converts dates to datetime
- Adds budget column from category mappings
- Filters to expenses only
- Removes author column

