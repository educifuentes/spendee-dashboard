"""
Data cleaning module for Spendee transaction exports.
"""
import pandas as pd
import json
from pathlib import Path


def load_budgets():
    """Load budget category mappings from JSON file."""
    budgets_path = Path(__file__).parent.parent / "constants" / "budgets.json"
    with open(budgets_path, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_transactions(input_path, output_path):
    """
    Clean and transform Spendee transaction data.
    
    Args:
        input_path: Path to raw CSV file
        output_path: Path to save cleaned CSV file
    """
    # Read raw data
    df = pd.read_csv(input_path)
    
    # Rename columns: 'Category name' -> 'category' and lowercase all
    df.columns = df.columns.str.lower()
    df = df.rename(columns={"category name": "category"})
    
    # Convert amount to absolute values
    df["amount"] = df["amount"].abs()
    
    # Convert date to datetime
    df["date"] = pd.to_datetime(df["date"])
    
    # Load budget mappings
    budgets = load_budgets()
    
    # Add budget column by mapping from category
    df["budget"] = df["category"].map(budgets).fillna("Otros")
    
    # Filter to only expenses
    df = df[df["type"].str.lower() == "expense"].copy()
    
    # Drop author column
    if "author" in df.columns:
        df = df.drop(columns=["author"])
    
    # Save cleaned data
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    return df


if __name__ == "__main__":
    # Run cleaning if executed directly
    input_file = Path(__file__).parent.parent / "data" / "raw" / "transactions_export_2025-12-19_main-clp.csv"
    output_file = Path(__file__).parent.parent / "data" / "clean" / "expenses_main-clp_clean.csv"
    df = clean_transactions(input_file, output_file)
    print(f"Cleaned data saved to {output_file}")
    print(f"DataFrame shape: {df.shape[0]} rows, {df.shape[1]} columns")

