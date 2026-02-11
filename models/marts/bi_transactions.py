import pandas as pd

from models.marts.cloud_sql._stg_cloud_sql__transactions import stg_cloud_sql__transactions

from utilities.constants.budgets import BUDGETS
from utilities.data_transformations.periods import create_period_columns
from utilities.data_transformations.universal_amount import create_universal_amount

def bi_transactions():
    df = stg_cloud_sql__transactions()

    # new columns
    df = create_period_columns(df)
    df = create_universal_amount(df)

    # Enrich with budget category mapping
    df["budget"] = df["category"].map(BUDGETS).fillna("Otros")
    
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