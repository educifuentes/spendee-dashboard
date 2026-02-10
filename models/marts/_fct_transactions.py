
import pandas as pd

from models.staging._stg_spendee__transactions import stg_spendee__transactions

from utilities.transforms import create_period_columns, create_universal_amount



def fct_transactions() -> pd.DataFrame:

    df = stg_spendee__transactions()
    
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


