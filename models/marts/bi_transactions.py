import pandas as pd

from models.marts._fct_transactions import fct_transactions

from utilities.data_transformations.enrichment import create_period_columns, create_universal_amount
from utilities.constants.budgets import BUDGETS


def bi_transactions():
    df = fct_transactions()

    # Enrich with budget category mapping
    df["budget"] = df["category"].map(BUDGETS).fillna("Otros")
    
    # Add  derived columns
    df = create_period_columns(df)
    df = create_universal_amount(df)

    # transform
    df["amount"] = df["amount"].abs()

    # drop columns
    df = df.drop(columns=["author"])
    
    # Reorder columns: place amount_universal_clp after currency
    cols = df.columns.tolist()
    if "amount_universal_clp" in cols and "currency" in cols:
        cols.remove("amount_universal_clp")
        currency_index = cols.index("currency")
        cols.insert(currency_index + 1, "amount_universal_clp")
        df = df[cols]
    return df