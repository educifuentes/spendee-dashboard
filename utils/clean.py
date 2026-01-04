"""
Data cleaning module for Spendee transaction exports.
"""
import hashlib
import json
import pandas as pd
from pathlib import Path
from pprint import pprint


# ==========================================
# Configuration Loading
# ==========================================

EXPORT_DATE = "2026-01-04"
WALLETS = ["main-clp", "pasivos", "unfcu"]

INPUT_FILES = [f"transactions_export_{EXPORT_DATE}_{wallet}.csv" for wallet in WALLETS]

OUTPUT_FILE = Path(__file__).parent.parent / "data" / "clean" / f"transactions_clean_{EXPORT_DATE}.csv"


def load_budgets():
    """Load budget category mappings from JSON file."""
    budgets_path = Path(__file__).parent.parent / "constants" / "budgets.json"
    with open(budgets_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==========================================
# Main Cleaning Logic
# ==========================================

def clean_transactions(input_path, output_path):
    """
    Clean and transform Spendee transaction data.
    
    Args:
        input_path: Path to raw CSV file
        output_path: Path to save cleaned CSV file
    """
    # ------------------------------------------
    # 1. Load & Normalize
    # ------------------------------------------
    # Define raw data directory
    raw_dir = Path(__file__).parent.parent / "data" / "raw"

    # Load first file
    df = pd.read_csv(raw_dir / input_path[0])

    # Append remaining files
    for file in input_path[1:]:
        temp_df = pd.read_csv(raw_dir / file)
        df = pd.concat([df, temp_df], ignore_index=True)
    
    # Rename columns: 'Category name' -> 'category' and lowercase all
    df.columns = df.columns.str.lower()
    df = df.rename(columns={"category name": "category"})
    
    # ------------------------------------------
    # 2. Data Transformations
    # ------------------------------------------
    # Convert amount to absolute values
    df["amount"] = df["amount"].abs()
    
    # Convert date to datetime
    df["date"] = pd.to_datetime(df["date"])
    
    # ------------------------------------------
    # 3. Enrichment (Budgets)
    # ------------------------------------------
    # Load budget mappings
    budgets = load_budgets()
    
    # Add budget column by mapping from category
    df["budget"] = df["category"].map(budgets).fillna("Otros")
    
    # ------------------------------------------
    # 4. Filtering & Cleanup
    # ------------------------------------------
    # Filter to only expenses
    df = df[df["type"].str.lower() == "expense"].copy()
    
    # Drop author column
    if "author" in df.columns:
        df = df.drop(columns=["author"])
    
    # ------------------------------------------
    # 5. Deduplication Logic
    # ------------------------------------------
    # Add record hash for duplicate detection
    df = add_record_hash(df)
    
    # ------------------------------------------
    # 6. Export
    # ------------------------------------------
    # Save cleaned data
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    return df

# ==========================================
# Helper Functions
# ==========================================

def _stable_str(x) -> str:
    if pd.isna(x):
        return ""
    return str(x).strip()

def add_record_hash(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a deterministic hash from the transaction content.
    This prevents duplicates even when multiple rows share the same date.
    """
    def row_hash(r) -> str:
        parts = [
            _stable_str(r["date"]),
            _stable_str(r["wallet"]),
            _stable_str(r["type"]),
            _stable_str(r["category"]),
            _stable_str(r["amount"]),
            _stable_str(r["currency"]),
            _stable_str(r.get("note", "")),
            _stable_str(r.get("labels", "")),
            _stable_str(r["budget"]),
        ]
        payload = "|".join(parts).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    df = df.copy()
    df["record_hash"] = df.apply(row_hash, axis=1)
    return df


# ==========================================
# Main Execution
# ==========================================

if __name__ == "__main__":
    # Run cleaning if executed directly

    df = clean_transactions(INPUT_FILES, OUTPUT_FILE)

    # Print a summary of the exported DataFrame
    print("\n--- Cleaned Data Summary ---")
    pprint("Columns:  ")
    pprint(list(df.columns))

    print(df.head())
    print(f"\nTotal expenses: {df['amount'].sum():,.2f}")
    print(f"Number of unique categories: {df['category'].nunique()}")
    print(f"Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")


    print(f"Cleaned data saved to {OUTPUT_FILE}")
    print(f"DataFrame shape: {df.shape[0]} rows, {df.shape[1]} columns")
