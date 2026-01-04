"""
Data cleaning module for Spendee transaction exports.
"""
import hashlib
import json
from datetime import datetime
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
    # Check for duplicates before saving
    check_duplicates(df)

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


def check_duplicates(df: pd.DataFrame):
    """Check for duplicate record hashes and print warning if found."""
    print(f"\nChecking for duplicates...")
    duplicates = df[df.duplicated(subset=["record_hash"], keep=False)]
    if not duplicates.empty:
        print(f"Found {len(duplicates)} rows with duplicate record_hash:")
        print(duplicates[["date", "wallet", "type", "category", "amount", "currency", "note", "labels", "budget"]])
        print(f"WARNING: {len(duplicates)} duplicates found, please edit data on source app")
    else:
        print("No duplicates found based on record_hash.")


def log_export_stats(df: pd.DataFrame, output_path: Path):
    """
    Append export statistics to a log file in the logs directory.
    """
    log_path = Path(__file__).parent.parent / "logs" / "export_log.txt"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = len(df)
    total_amount = df["amount"].sum()
    date_range = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}" if not df.empty else "N/A"
    
    log_entry = (
        f"[{timestamp}] Exported {rows} rows to {output_path.name}\n"
        f"    - Total Amount: {total_amount:,.2f}\n"
        f"    - Date Range: {date_range}\n"
        f"    - Source Date: {EXPORT_DATE}\n"
        f"--------------------------------------------------\n"
    )
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    print(f"Log entry added to {log_path}")


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

    # Log the export
    log_export_stats(df, OUTPUT_FILE)
