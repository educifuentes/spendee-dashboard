import pandas as pd
from pathlib import Path

# Configuration
EXPORT_DATE = "2026-01-04"
INPUT_FILE = Path(__file__).parent.parent / "data" / "clean" / f"transactions_clean_{EXPORT_DATE}.csv"

def main():
    # Load clean data
    print(f"Loading data from: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)

    # Identify non-numeric columns
    columns_to_analyze = ['date',
 'wallet',
 'type',
 'category',
 'currency',
 'labels',
 'budget']
    
    # Print value counts for each non-numeric column
    for col in columns_to_analyze:
        print(f"\n--- Value Counts: {col} ---")
        print(df[col].value_counts())

if __name__ == "__main__":
    main()