import pandas as pd

from utilities.data_connection_cloud_sql import load_stg_transactions


def stg_spendee__transactions():
    df = load_stg_transactions()
    
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    return df