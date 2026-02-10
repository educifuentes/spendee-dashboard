
import pandas as pd

from models.staging._stg_spendee__transactions import stg_spendee__transactions

from utilities.transforms import create_period_columns, create_universal_amount



def fct_transactions() -> pd.DataFrame:

    df = stg_spendee__transactions()

    # def load_budgets():
    # """Load budget category mappings from JSON file."""
    # budgets_path = Path(__file__).parent.parent.parent / "utilities" / "constants" / "budgets.json"
    # with open(budgets_path, "r", encoding="utf-8") as f:
    #     return json.load(f)


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
    
    # Create new columns
    df = create_period_columns(df)
    df = create_universal_amount(df)

    # reorder columns
    cols = df.columns.tolist()
    if "amount" in cols and "amount_universal_clp" in cols:
        cols.remove("amount_universal_clp")
        amount_index = cols.index("currency")
        cols.insert(amount_index + 1, "amount_universal_clp")
        df = df[cols]

    return df


