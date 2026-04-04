import pandas as pd


def exp_income_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters transactions to Income type only.
    Returns a DataFrame of income transactions for display.
    """
    return df[df["type"] == "Income"].copy()
