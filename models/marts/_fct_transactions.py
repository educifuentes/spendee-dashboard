import pandas as pd

from models.staging._stg_spendee__transactions import stg_spendee__transactions

from utilities.data_transformations.periods import create_period_columns
from utilities.data_transformations.add_record_hash import add_record_hash


def fct_transactions():
    # Load staging data
    df = stg_spendee__transactions()

    # rename columns
    rename_dict = {
        "Date": "date",
        "Wallet": "wallet",
        "Type": "type",
        "Category name": "category",
        "Amount": "amount",
        "Author": "author",
        "Currency": "currency",
        "Note": "note",
        "Labels": "labels",
    }

    df.rename(columns=rename_dict, inplace=True)

    # Add record hash and ID
    df = add_record_hash(df, columns=["date", "wallet", "type", "category", "amount", "note"])

    df["id"] = df.index
    
    return df

