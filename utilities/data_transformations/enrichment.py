import pandas as pd
from utilities.data_transformations.rates import get_usd_clp_rates_map

def create_period_columns(df):
    """Create day, week, month, year columns from date."""
    df["day"] = df["date"].dt.strftime("%Y-%m-%d")
    # Use isocalendar to correctly handle year boundaries for weeks
    iso = df["date"].dt.isocalendar()
    df["week"] = iso.year.astype(str) + "-W" + iso.week.astype(str).str.zfill(2)
    df["month"] = df["date"].dt.strftime("%Y-%m")
    df["year"] = df["date"].dt.year
    return df

def create_universal_amount(df):
    """
    Create amount_universal column in CLP.
    If currency is USD, converts to CLP using approximate monthly rates.
    """
    if "currency" not in df.columns:
        df["amount_universal"] = df["amount"]
        return df

    rates_map = get_usd_clp_rates_map()

    df["rate"] = df["date"].dt.strftime("%Y-%m").map(rates_map).fillna(900)
    df["amount_universal_clp"] = df.apply(lambda x: x["amount"] * x["rate"] if x["currency"] == "USD" else x["amount"], axis=1).round(0)

    return df.drop(columns=["rate"])
