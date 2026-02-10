
import pandas as pd


def stg_spendee__transactions() -> pd.DataFrame:
    """data of all wallets into one transaction sdataframe"""

    # input files in seeds wallets

    df = pd.read_csv("./seeds/transactions/main-clp.csv")
    
    
    return df


