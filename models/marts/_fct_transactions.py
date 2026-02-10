"""
Fact table for transactions.
Enriches staging data with budget categories and derived columns.
"""
import pandas as pd

from models.staging._stg_spendee__transactions import stg_spendee__transactions

from utilities.transforms import create_period_columns, create_universal_amount
from utilities.constants.budgets import BUDGETS


def fct_transactions() -> pd.DataFrame:
    """
    Create the transactions fact table.
    
    Transforms:
        - Maps categories to budget groups
        - Adds period columns (year, month, quarter)
        - Adds universal amount in CLP
        - Reorders columns for better readability
    
    Returns:
        pd.DataFrame: Enriched transactions fact table
    """
    # Load staging data
    df = stg_spendee__transactions()
    
    # Enrich with budget category mapping
    df["budget"] = df["category"].map(BUDGETS).fillna("Otros")
    
    # Add derived columns
    df = create_period_columns(df)
    df = create_universal_amount(df)
    
    # Reorder columns: place amount_universal_clp after currency
    cols = df.columns.tolist()
    if "amount_universal_clp" in cols and "currency" in cols:
        cols.remove("amount_universal_clp")
        currency_index = cols.index("currency")
        cols.insert(currency_index + 1, "amount_universal_clp")
        df = df[cols]
    
    return df

