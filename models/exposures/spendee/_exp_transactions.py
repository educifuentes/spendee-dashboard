import pandas as pd

from helpers.sqlite_loader import load_from_sqlite
from helpers.data_transformations.universal_amount import create_universal_amount
from helpers.constants.budgets import BUDGETS


_TABLE = "stg_transaction"


def exp_transactions():


    df = load_from_sqlite(_TABLE)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    # new columns

    df = create_universal_amount(df)

    # Enrich with budget category mapping
    df["budget"] = df["category"].map(BUDGETS).fillna("Otros")

    cols = df.columns.tolist()
    if "amount_universal_clp" in cols and "currency" in cols:
        cols.remove("amount_universal_clp")
        currency_index = cols.index("currency")
        cols.insert(currency_index + 1, "amount_universal_clp")
        df = df[cols]

    return df