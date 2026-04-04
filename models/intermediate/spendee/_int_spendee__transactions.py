import pandas as pd

from models.staging.spendee._stg_spendee__transactions import stg_spendee__transactions

from helpers.constants.budgets import BUDGETS
from helpers.data_transformations.periods import create_period_columns
from helpers.data_transformations.universal_amount import create_universal_amount

def int_spendee__transactions():

    # rename
    df = stg_spendee__transactions()
    df = df.rename(columns={"Date": "date", "Wallet": "wallet", "Type": "type", "Category name": "category", "Amount": "amount", "Currency": "currency", "Note": "note", "Labels": "labels", "Author": "author"})

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