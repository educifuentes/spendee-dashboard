import pandas as pd
from helpers.data_transformations.rates import get_usd_clp_rates_map

def create_universal_amount(df):
    """
    Create amount_universal column in CLP.
    If currency is USD, converts to CLP using approximate monthly rates.
    """
    if "currency" not in df.columns:
        df["amount_universal"] = df["amount"].abs()
        return df

    rates_map = get_usd_clp_rates_map()

    df["rate"] = df["date"].dt.strftime("%Y-%m").map(rates_map).fillna(900)
    df["amount_universal_clp"] = df.apply(lambda x: x["amount"] * x["rate"] if x["currency"] == "USD" else x["amount"], axis=1).round(0).abs()

    return df.drop(columns=["rate"])
